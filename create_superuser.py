#!/usr/bin/env python3
import sys
import os
# Add backend path to sys.path if running from ZYNAPSE root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.database import get_session, engine, SQLModel
from backend.models.user import UserCreate
from backend.services import user_service
from backend.services import plan_service # Import plan_service to create default plans

def main():
    print("Ensuring database and tables exist...")
    SQLModel.metadata.create_all(engine)

    print("Attempting to create default plans and superuser...")
    # Use context manager for session
    with next(get_session()) as session:
        # Create default plans first
        print("Checking/Creating default plans...")
        plan_service.create_default_plans(session)
        print("Default plans checked/created.")

        # Define superuser details (Updated with user's request)
        email = "cleitonneri04@gmail.com"
        password = "dexter" # User provided password

        # Check if user already exists
        user = user_service.get_user_by_email(session, email=email)
        if not user:
            print(f"Creating superuser {email}...")
            # Assign a default plan (e.g., Enterprise)
            enterprise_plan = plan_service.get_plan_by_name(session, name="Enterprise")
            plan_id = enterprise_plan.id if enterprise_plan else None
            if not plan_id:
                print("Warning: Enterprise plan not found. Superuser might lack plan features.")

            user_in = UserCreate(
                email=email,
                password=password,
                full_name="Cleiton Neris", # Assuming a name, user can change later
                is_superuser=True,
                is_active=True,
                plan_id=plan_id # Assign Enterprise plan ID
            )
            user_service.create_user(db=session, user=user_in)
            print(f"Superuser 	'{email}	' created successfully with password 	'{password}	'.")
        else:
            print(f"User 	'{email}	' already exists. Checking if superuser status needs update...")
            if not user.is_superuser:
                print(f"Updating user 	'{email}	' to be a superuser.")
                # Simple update example, might need a dedicated service function
                user.is_superuser = True
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"User 	'{email}	' is now a superuser.")
            else:
                print(f"User 	'{email}	' is already a superuser.")

if __name__ == "__main__":
    main()


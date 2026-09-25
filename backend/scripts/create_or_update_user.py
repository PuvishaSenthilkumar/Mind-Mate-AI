import sys
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models, auth


def create_or_update(email: str, new_password: str, full_name: str = 'Swetha'):
    db: Session = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            user.hashed_password = auth.hash_password(new_password)
            db.add(user)
            db.commit()
            print('UPDATED')
            return 0
        # create user
        user = models.User(full_name=full_name, email=email, hashed_password=auth.hash_password(new_password))
        db.add(user)
        db.commit()
        db.refresh(user)
        print('CREATED', user.id)
        return 0
    except Exception as e:
        print('ERROR', e)
        return 2
    finally:
        db.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: create_or_update_user.py email new_password [full_name]')
        sys.exit(1)
    email = sys.argv[1]
    new_password = sys.argv[2]
    full_name = sys.argv[3] if len(sys.argv) > 3 else 'Swetha'
    code = create_or_update(email, new_password, full_name)
    sys.exit(code)

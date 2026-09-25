import sys
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models, auth


def reset_password(email: str, new_password: str):
    db: Session = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            print('USER_NOT_FOUND')
            return 2
        user.hashed_password = auth.hash_password(new_password)
        db.add(user)
        db.commit()
        print('PASSWORD_UPDATED')
        return 0
    except Exception as e:
        print('ERROR', e)
        return 3
    finally:
        db.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: reset_password.py email new_password')
        sys.exit(1)
    email = sys.argv[1]
    new_password = sys.argv[2]
    code = reset_password(email, new_password)
    sys.exit(code)

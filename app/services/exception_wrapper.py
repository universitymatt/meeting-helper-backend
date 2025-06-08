from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


def handle_db_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTPException without modification
            raise
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred",
            )

    return wrapper

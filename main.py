from fastapi import FastAPI, HTTPException, Depends, status
from database import UpdateUser,UpdateExpense, create_db_and_tables, engine, User, Expense
from sqlmodel import Session, select

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/users")
def get_users(
    skip: int = 0,
    limit: int = 5,
    session: Session = Depends(get_session)
):
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users

@app.get("/expenses")
def get_expenses(
    session: Session = Depends(get_session),
    min_amount: int | None = None,
    skip: int = 0,
    limit: int = 20
    ):

    statement = select(Expense)
    if min_amount is not None:
        statement = statement.where(Expense.amount >= min_amount)

    statement = statement.offset(skip).limit(limit)
    expenses = session.exec(statement).all()
    return expenses

    

@app.get("/users/{user_id}/expenses")
def get_expenses_by_userid(user_id: int, session: Session = Depends(get_session)):
    statement = select(Expense).where(Expense.user_id == user_id)
    expenses = session.exec(statement).all()
    return expenses

@app.post("/users/")
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post("/expenses/")
def create_expense(expense: Expense, session: Session = Depends(get_session)):
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense

@app.delete("/users/{user_id}/delete")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="მომხმარებელი ვერ მოიძებნა"
        )
    statement = select(Expense).where(Expense.user_id == user_id)
    users_all_expense = session.exec(statement).all()

    for expense in users_all_expense:
        session.delete(expense)
    
    session.delete(user)
    session.commit()
    return {
            "message": "მომხმარებელი წარმატებით წაიშალა.",
            "user": user,
            "expenses": users_all_expense
        }

@app.delete("/expenses/{expense_id}/delete")
def delete_expense(expense_id:int, session: Session = Depends(get_session)):
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="ხარჯი ვერ მოიძებნა"
        )
    session.delete(expense)
    session.commit()

    return {
        "message": "ხარჯი წარმატებიტ წაიშალა."
    }


@app.delete("/clear")
def clear(session: Session = Depends(get_session)):
    expenses = session.exec(select(Expense)).all()
    users = session.exec(select(User)).all()

    if not expenses and not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ბაზა ცარიელია."
        )

    for expense in expenses:
        session.delete(expense)

    for user in users:
        session.delete(user)
    
    session.commit()

    return {"message": "ყველაფერი წაიშალა."}


@app.patch("/users/{user_id}")
def change_user(
    user_id: int,
    user_data: UpdateUser,
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="მომხმარებელი ვერ მოიძებნა."
        )

    update_data = user_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@app.patch("/expenses/{expense_id}")
def change_expense(
    expense_id: int,
    expense_data: UpdateExpense,
    session: Session = Depends(get_session)
):
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="ხარჯი ვერ მოიძებნა."
        )

    expense_data_to_change = expense_data.model_dump(exclude_unset=True)
    for key, value in expense_data_to_change.items():
        setattr(expense, key, value)

    session.add(expense)
    session.commit()
    session.refresh(expense)

    return expense
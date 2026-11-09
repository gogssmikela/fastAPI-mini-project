from sqlmodel import SQLModel, create_engine, Field, Relationship

DATABASE_URL = "sqlite:///expenses.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

class UpdateUser(SQLModel):
    username: str | None = None

class UpdateExpense(SQLModel):
    title: str | None = None
    amount: float | None = None

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str

class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    amount: float
    user_id: int 
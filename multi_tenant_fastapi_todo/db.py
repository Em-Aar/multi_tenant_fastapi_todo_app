from sqlmodel import SQLModel, Field, create_engine, Session, select
from dailydo_todo_app import setting


# create model for user table
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    password: str

# create model for todo table
class Todo (SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(index=True, min_length=3, max_length=54)
    is_completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id")

# create connection string to be use while creating engine
connection_string: str = str(setting.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")

# create engine
engine = create_engine(connection_string, connect_args={
                       "sslmode": "require"}, pool_recycle=300, pool_size=10)

# create session
def get_session():
    with Session(engine) as session:
        yield session


### Setup

To set it up, you simple need to install the python dependencies. This codebases uses python 3.9 so create a venv with that in mind.

Note that this is NOT a flask application, but a FastAPI application.

### SQLAlchemy and migrations

Unlike a normal flask application, this uses SQLAlchemy more directly. This means that defining the engine and models 
works differently than it would in flask. You have to create the engine yourself and then manage the sessions. Here we 
manage the sessions using FastAPISessionMaker.

Before running these commands you may not to sent the `SECRETS_PATH` environment variable.

In Linux use: `export SECRETS_PATH=<absolute-path-to-secrets.json>`

In Windows use: `set SECRETS_PATH=<absolute-path-to-secrets.json>`


Run following commands:

`alembic revision --autogenerate`

`alembic upgrade head`

Please read the alembic migration documentation for more info.

**In case of errors with migrations**

1. Truncate table alembic_version with command `truncate table alembic_version;`

2. Delete all files from alembic/version/ folder. NOTE: Do not delete the folder, just the files inside.

3. Run `alembic revision --autogenerate`

4. Run `alembic upgrade head`

### Pytest setup

Set default test runner to pytest

Go to Settings > Tools > Python Integregrated Tools. Under Testing, set default test runner to pytest

Please add the following arguments to your pytest run configuration template (in Additional Arguments):

--tb=native --capture=tee-sys 

### Handling validation errors

Standard way of handling errors is to raise an fastAPI.HTTPException

### for frontend- response handling code
    # for error
    if not stat:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": "Error: " + msg, "body": "Error: " + msg})
        )

    # for success msg
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=jsonable_encoder({"detail": "Success: " + msg, "body": "Error: " + msg}))


### Pytest setup

Please add the following arguments to your pytest run configuration template (in Additional Arguments):

### DBApi Setup

Note that all write functions i.e. functions that write to the DB, must have two optional parameters:

1. `commit=True` (defaulted to True) so that if a caller wants to commit, they can do so without specifying

2. `session=None` This is to make sure that objects that need foriegn keys to also be saved can be saved appropriately in the same session / transaction

All read queries should have the session parameter.

### Sass/SCSS

https://www.digitalocean.com/community/tutorials/using-sass-with-the-angular-cli

https://sass-lang.com/guide

### Handling validation errors

Standard way of handling errors is to raise an fastAPI.HTTPException

### Structure

#### API

Will have all the API routes

Routes will have minimal code, it will call functions to execute main logic.

Many smaller files are better than bigger files

API - module - route files

Each module folder in the api folder will have a DTOs folder for DTOs. See section on DTOs for more

#### DATA


Anything to do with DB

models folder will have all the models

Each model will have its own file

DBAPi will have read modules and write modules. ALl code for read queries will be in separate packages from write queries.

Each function (read or write) will have the dbapi_exception_handler decorator

Each function will also have a session=None parameter

Read queries must have a close_session=True parameter (which will be read by dbapi_exception_handler) to close the session

DB Session will be initialized using:

```
db = session
if session is None:
    db = next(get_db())

```

Each write query function will also have a commit=True parameter. Used as:

```
if commit:
    db.commit()
```

If a function has more than 5 args (including session and commit), use a DTO class

If using sqlalchemy relationships, please use the parameter `lazy='subquery'` when defining a relationship.

For example:

```
class Company(ModelBase):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

class User(ModelBase):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # other fields
    company = relationship('Companies', lazy='subquery', # other params) 
```

When updating using update functions, please also use `db.add(object_to_update)` before commit() or flush()

Also please use existing sessions when updating two objects which may depend on each other.

Session management SHOULD NOT be done in these files. Session management instead should be done in the logic layer.

Use the `close_session=False` parameter if you want to keep sessions open after read queries (for example in case of updates)

#### LOGIC

It will call the dbapi functions.

It will have requirements / business logic code.

Structure:

logic -> module name -> individual files


###### Session management

Session management should be done in the logic layer. The logic layer is where we aggregate all the dbapi functions and use them to implement our business logic.

For example, say we want to add a user with a company:

```
# Dummy function that takes user details and company details
# It creates a new company and then updates an existing user
# or creates a new user and adds to new company to it.
def add_user_with_company(dto: UserWithCompanyDTO):
    db = next(get_db())

    # Check if user exists
    existing_user = find_user_by_id(user_id, session=db)

    # Create a new company
    company_id = add_company(dto.company_details, session=db, commit=False)

    # If user exists, set company_id to new company
    if existing_user:
        existing_user.company_id = company_id
        db.add(existing_user)
    else:
        # Else create a new user with this company id
        dto.company_id = company_id
        user = add_user(dto, commit=True)

    db.close()

```


#### Using DTOs

DTO stands for "Data Transfer Object" and it is basically just a simple class that is used to group together a 
bunch of variables, or convert the request json to a usable python object. This is the basic concept of the DTO.

Each request and function CAN HAVE THEIR OWN DTO. You don't necessarily need to reuse dtos unless you can be sure that
changing it won't break both functions.

Return values from functions can also be DTOs. For example, if you have a function that returns 2 variables with different
values based on different circumstances, you can put those in a dto and return that.

Please keep the following in mind:

Do NOT use the the same DTO for API requests and responses. 

If a function has more than 5 parameters, put all the parameters in a FunctionNameParamsDTO and use that as a 
parameter instead.

If a function has more than 1 return value, consider using a DTO as the return value.

DO NOT use the same DTO for params and return values.

# Необходимо создать базу данных для интернет-магазина. База данных должна состоять из трёх таблиц: товары, заказы и пользователи.
# — Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.
# — Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.
# — Таблица «Пользователи» должна содержать информацию о зарегистрированных пользователях магазина.
# • Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.
# • Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
# • Таблица товаров должна содержать следующие поля: id (PRIMARY KEY), название, описание и цена.

# Создайте модели pydantic для получения новых данных и возврата существующих в БД для каждой из трёх таблиц (итого шесть моделей).
# Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API (итого 15 маршрутов).
# * Чтение всех
# * Чтение одного
# * Запись
# * Изменение
# * Удаление

# Данная промежуточная аттестация оценивается по системе "зачет" / "не зачет"

# "Зачет" ставится, если Слушатель успешно выполнил задание.
# "Незачет" ставится, если Слушатель не выполнил задание.

# Критерии оценивания:
# 1 - Слушатель создал базу данных для интернет-магазина. База данных должна состоять из трёх таблиц: товары, заказы и пользователи.
# — Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.
# — Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.
# — Таблица «Пользователи» должна содержать информацию о зарегистрированных пользователях магазина.


from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field
import databases
import sqlalchemy
import datetime


DATABASE_URL = 'sqlite:///mydatabase.db'

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[SQLAlchemy Tables]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('first_name', sqlalchemy.String(15)),
    sqlalchemy.Column('last_name', sqlalchemy.String(20)),
    sqlalchemy.Column('email', sqlalchemy.String(50), unique=True),
    sqlalchemy.Column('password', sqlalchemy.String(20))
)


products = sqlalchemy.Table(
    'products',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(50)),
    sqlalchemy.Column('description', sqlalchemy.String(1000)),
    sqlalchemy.Column('cost', sqlalchemy.Float),
)


orders = sqlalchemy.Table(
    'orders',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('product_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column('order_date', sqlalchemy.Date),
    sqlalchemy.Column('order_status', sqlalchemy.String(20))
)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[Pydantic Models]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserIn(BaseModel):
    first_name: str = Field(..., max_length=15)
    last_name: str = Field(..., max_length=20)
    email: str = Field(..., max_length=50)
    password: str = Field(..., max_length=20)


class User(BaseModel):
    id: int
    first_name: str = Field(..., max_length=15)
    last_name: str = Field(..., max_length=20)
    email: str = Field(..., max_length=50)
    password: str = Field(..., max_length=20)


class OrderIn(BaseModel):
    user_id: int
    product_id: int
    order_date: datetime.date
    order_status: str = Field(..., max_length=20)


class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    order_date: datetime.date
    order_status: str = Field(..., max_length=20)


class ProductIn(BaseModel):
    name: str = Field(..., max_length=50)
    description: str = Field(..., max_length=1000)
    cost: float = Field(..., ge=1, le=1_000_000)


class Product(BaseModel):
    id: int
    name: str = Field(..., max_length=50)
    description: str = Field(..., max_length=1000)
    cost: float = Field(..., ge=1, le=1_000_000)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[Events]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[CRUD Users]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.post('/users/', response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(first_name=user.first_name, last_name=user.last_name, email=user.email, password=user.password)
    last_record_id = await database.execute(query)
    return {**user.dict(), 'id': last_record_id}


@app.get('/users/', response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/users/{user_id}', response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.put('/users/{user_id}', response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), 'id': user_id}


@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': f'User {user_id} deleted'}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[CRUD Orders]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.post('/orders/', response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(user_id=order.user_id, product_id=order.product_id, order_date=order.order_date, order_status=order.order_status)
    last_record_id = await database.execute(query)
    return {**order.dict(), 'id': last_record_id}


@app.get('/orders/', response_model=List[Order])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get('/orders/{order_id}', response_model=Order)
async def read_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.put('/orders/{order_id}', response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
    query = orders.update().where(orders.c.id == order_id).values(**new_order.dict())
    await database.execute(query)
    return {**new_order.dict(), 'id': order_id}


@app.delete('/orders/{order_id}')
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': f'Order {order_id} deleted'}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[CRUD Products]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.post('/products/', response_model=Product)
async def create_product(product: ProductIn):
    query = products.insert().values(name=product.name, description=product.description, cost=product.cost)
    last_record_id = await database.execute(query)
    return {**product.dict(), 'id': last_record_id}


@app.get('/products/', response_model=List[Product])
async def read_products():
    query = products.select()
    return await database.fetch_all(query)

    
@app.get('/products/{product_id}', response_model=Product)
async def read_product(product_id: int):
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)


@app.put('/products/{product_id}', response_model=Product)
async def update_product(product_id: int, new_product: ProductIn):
    query = products.update().where(products.c.id == product_id).values(**new_product.dict())
    await database.execute(query)
    return {**new_product.dict(), 'id': product_id}


@app.delete('/products/{product_id}')
async def delete_product(product_id: int):
    query = products.delete().where(products.c.id == product_id)
    await database.execute(query)
    return {'message': f'Product {product_id} deleted'}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
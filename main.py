# Необходимо создать API для управления списком задач. Каждая задача должна содержать заголовок и описание. Для каждой задачи должна быть возможность указать статус (выполнена/не выполнена).

# API должен содержать следующие конечные точки:
# — GET /tasks — возвращает список всех задач.
# — GET /tasks/{id} — возвращает задачу с указанным идентификатором.
# — POST /tasks — добавляет новую задачу.
# — PUT /tasks/{id} — обновляет задачу с указанным идентификатором.
# — DELETE /tasks/{id} — удаляет задачу с указанным идентификатором.

# Для каждой конечной точки необходимо проводить валидацию данных запроса и ответа. Для этого использовать библиотеку Pydantic.

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from typing import Optional
from pydantic import BaseModel
import pandas as pd


app = FastAPI()

tasks = []


class Task(BaseModel):
    id: int
    title: str
    content: str
    status: Optional[str] = 'Не выполнена'


@app.post('/tasks/', response_model=Task)
async def create_task(task: Task):
    task_id = len(tasks) + 1
    task.id = task_id
    tasks.append(task)
    return task


@app.get('/tasks/', response_class=HTMLResponse)
async def show_tasks():
    task_table = pd.DataFrame([vars(task) for task in tasks]).to_html()
    return task_table

@app.get('/tasks/{task_id}', response_class=HTMLResponse)
async def show_task(task_id: int):
    for i in range(len(tasks)):
        if task_id == tasks[i].id:
            task_table = pd.DataFrame(tasks[i]).to_html()
            return task_table

@app.put('/tasks/{task_id}', response_model=Task)
async def change_task(task_id: int, task: Task):
    for i, item in enumerate(tasks):
        if item.id == task_id:
            task.id = task_id
            tasks[i] = task
            return task

@app.delete('/tasks/{task_id}', response_model=Task)
async def delete_task(task_id: int, task: Task):
    for i, item in enumerate(tasks):
        if item.id == task_id:
            tasks.pop(i)
            return task
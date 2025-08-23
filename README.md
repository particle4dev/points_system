## 📦 Create a New Project

```bash
poetry new points_system
poetry add alembic sqlmodel dotenv pydantic pydantic-settings
```

## ⚙️ Set Up Alembic

```bash
cd src/
poetry run alembic init migration
```

## 🚀 Start the Project

Navigate to your lesson directory and start the Docker containers:

```bash
cd ~/workspace/jeffhl-ai/python-training/lessons/points_system/
docker compose up -d
```

## 🔄 Apply Database Migrations

To apply the latest schema changes to your database:

```bash
cd src
poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add UserPoint table"
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "Add UserPointHistory table"


poetry run alembic downgrade base # This command will undo all migrations.
```

## ⚠️ Common Issues & Solutions

### 🔸 Error: `ModuleNotFoundError: No module named 'psycopg'`

📘 Refer to the [psycopg documentation](https://www.psycopg.org).

✅ **Solution:** Install the required dependency. For new projects, it's recommended to use **psycopg3**:

```bash
poetry add psycopg[binary]
```

## Seed

```sh
cd src
PYTHONPATH=. poetry run python3 seed/cli.py create                # Seed default dev data
PYTHONPATH=. poetry run python3 seed/cli.py delete                # Delete dummy data
```

## References

- https://sqlmodel.tiangolo.com/#editor-support




<!-- poetry run alembic revision --autogenerate -m "Add PointsCampaign table" -->



poetry run alembic revision --autogenerate -m "Add Partner table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PartnerPool table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add Token table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PartnerUniswapV3LP table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PartnerUniswapV3Tick table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PartnerUniswapV3Event table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PartnerPoolUniswapV3 table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PointsCampaign table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PointsPointType table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PointsUserCampaignPoints table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Add PointsUserPoint table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Create PointsUserPoint summary trigger"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Create PointsUserPointHistory table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Create PointsUserPointHistory trigger"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Create PointsPartnerSnapshot table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Create PartnerUserPosition table"

poetry run alembic upgrade head

poetry run alembic revision --autogenerate -m "Create PartnerProtocolEvent table"


poetry env list


# Remove all the files of the current environment of the folder we are in
POETRY_LOCATION=`poetry env info -p` 
echo "Poetry is $POETRY_LOCATION"
rm -rf "$POETRY_LOCATION"

poetry env activate


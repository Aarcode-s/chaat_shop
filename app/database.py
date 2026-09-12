from decimal import Decimal

from sqlalchemy import create_engine, inspect, select, text
from fastapi import Depends
from typing import Annotated

from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)


def create_db_and_tables() -> None:
    """Create the schema and migrate the menu category column for old databases."""
    Base.metadata.create_all(bind=engine)
    if "category" not in {column["name"] for column in inspect(engine).get_columns("menu_items")}:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE menu_items "
                    "ADD COLUMN category VARCHAR(20) NOT NULL DEFAULT 'snacks'"
                )
            )
            category_groups = {
                "chaat": [
                    "Pani Puri",
                    "Bhel Puri",
                    "Sev Puri",
                    "Dahi Puri",
                    "Aloo Tikki Chaat",
                    "Papdi Chaat",
                    "Raj Kachori",
                ],
                "snacks": [
                    "Samosa",
                    "Kachori",
                    "Paneer Tikka",
                    "Vada Pav",
                    "Pav Bhaji",
                    "Masala Fries",
                    "Bread Pakora",
                    "Chilli Cheese Toast",
                ],
                "drinks": [
                    "Mango Lassi",
                    "Masala Chaas",
                    "Nimbu Soda",
                    "Jal Jeera",
                    "Ginger Tea",
                ],
            }
            for category, names in category_groups.items():
                placeholders = ", ".join(f":name_{index}" for index in range(len(names)))
                parameters = {f"name_{index}": name for index, name in enumerate(names)}
                parameters["category"] = category
                connection.execute(
                    text(
                        f"UPDATE menu_items SET category = :category "
                        f"WHERE name IN ({placeholders})"
                    ),
                    parameters,
                )


def seed_menu_items() -> None:
    """Insert the starter menu once, without overwriting existing menu data."""
    from app.models import MenuItem

    with session_local() as db:
        if db.execute(select(MenuItem.id).limit(1)).scalar_one_or_none() is not None:
            return

        menu_items = [
            ("Pani Puri", "chaat", "Crisp puris filled with spiced mint water and tangy chutney.", "70.00"),
            ("Bhel Puri", "chaat", "Puffed rice tossed with vegetables, chutneys, and crunchy sev.", "90.00"),
            ("Sev Puri", "chaat", "Crisp puris layered with potato, chutneys, and plenty of sev.", "95.00"),
            ("Dahi Puri", "chaat", "Soft puris with creamy yogurt, sweet chutney, and spices.", "110.00"),
            ("Aloo Tikki Chaat", "chaat", "Crispy potato patties topped with yogurt and bold chutneys.", "120.00"),
            ("Papdi Chaat", "chaat", "Crisp papdi, chickpeas, yogurt, chutneys, and fresh coriander.", "115.00"),
            ("Raj Kachori", "chaat", "A generously stuffed kachori with yogurt, chutneys, and sev.", "140.00"),
            ("Samosa", "snacks", "Golden pastry filled with warmly spiced potatoes and peas.", "45.00"),
            ("Kachori", "snacks", "Flaky, crisp pastry packed with a savoury lentil filling.", "50.00"),
            ("Paneer Tikka", "snacks", "Smoky marinated paneer grilled with peppers and onions.", "180.00"),
            ("Vada Pav", "snacks", "Spiced potato fritter in a soft bun with garlic chutney.", "80.00"),
            ("Pav Bhaji", "snacks", "Buttery buns served with rich vegetable bhaji and onions.", "130.00"),
            ("Masala Fries", "snacks", "Crispy fries dusted with our tangy house masala.", "95.00"),
            ("Bread Pakora", "snacks", "Batter-fried bread filled with seasoned potato.", "75.00"),
            ("Chilli Cheese Toast", "snacks", "Toasted bread with melted cheese, chilli, and herbs.", "125.00"),
            ("Mango Lassi", "drinks", "Thick, creamy yogurt drink blended with ripe mango.", "100.00"),
            ("Masala Chaas", "drinks", "Refreshing spiced buttermilk with coriander and cumin.", "60.00"),
            ("Nimbu Soda", "drinks", "Sparkling lime cooler served sweet, salty, or both.", "55.00"),
            ("Jal Jeera", "drinks", "Chilled cumin and mint cooler with a bright tangy finish.", "65.00"),
            ("Ginger Tea", "drinks", "Fragrant Indian tea brewed with fresh ginger and spices.", "50.00"),
        ]

        db.add_all(
            [
                MenuItem(
                    name=name,
                    category=category,
                    description=description,
                    price=Decimal(price),
                    is_available=True,
                )
                for name, category, description, price in menu_items
            ]
        )
        db.commit()


session_local = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = session_local()

    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[Session, Depends(get_db)]


class Base(DeclarativeBase):
    pass
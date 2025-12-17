from app.core.database import engine, Base
import app.models

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente")

if __name__ == "__main__":
    init_db()

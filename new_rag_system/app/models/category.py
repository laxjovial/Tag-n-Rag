from sqlalchemy import Column, Integer, String, Table, ForeignKey, relationship
from ..database import Base

# Association Table for the many-to-many relationship
document_category_association = Table(
    'document_category', Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    documents = relationship(
        "Document",
        secondary=document_category_association,
        back_populates="categories"
    )

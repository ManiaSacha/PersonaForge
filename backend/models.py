from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base
import json

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    personas = relationship("Persona", back_populates="owner")

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tone = Column(String)
    domain = Column(String)
    goals = Column(Text)  # Will store JSON string of goals array
    response_style = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="personas")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tone": self.tone,
            "domain": self.domain,
            "goals": json.loads(self.goals),
            "response_style": self.response_style
        }
    
    @classmethod
    def from_dict(cls, data, owner_id):
        return cls(
            name=data["name"],
            tone=data["tone"],
            domain=data["domain"],
            goals=json.dumps(data["goals"]),
            response_style=data["response_style"],
            owner_id=owner_id
        )

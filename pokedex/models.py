from pokedex import db, login_manager
from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Table, Column, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from flask_login import UserMixin
from typing import List
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
  return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  username: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
  email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
  password: Mapped[str] = mapped_column(String(100), nullable=False)
  firstname: Mapped[str] = mapped_column(String(25), nullable=True)
  lastname: Mapped[str] = mapped_column(String(25), nullable=True)
  avatar: Mapped[str] = mapped_column(String(25), default='avatar.png')
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

  types: Mapped[List['PokemonType']] = relationship(back_populates='user')
  pokemons: Mapped[List['Pokemon']] = relationship(back_populates='user')

  def __repr__(self):
    return f'<User: {self.username}>'
  
pokedex = Table(
  'pokedex',
  db.metadata,
  Column('type_id', Integer, ForeignKey('type.id'), primary_key=True),
  Column('pokemon_id', Integer, ForeignKey('pokemon.id'), primary_key=True)
)

class PokemonType(db.Model):
  __tablename__ = 'type'
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
  
  pokemons: Mapped[List['Pokemon']] = relationship(back_populates='types',
                                                   secondary=pokedex)
  user: Mapped[User] = relationship(back_populates='types')

  def __repr__(self):
    return f'<PokemonType: {self.name}>'
  

class Pokemon(db.Model):
  __tablename__ = 'pokemon'
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
  height: Mapped[str] = mapped_column(String(20), nullable=True)
  weight: Mapped[str] = mapped_column(String(20), nullable=True)
  description: Mapped[str] = mapped_column(Text, nullable=True)
  img_url: Mapped[str] = mapped_column(String(255), nullable=True)
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

  user: Mapped['User'] = relationship(back_populates='pokemons')
  types: Mapped[List[PokemonType]] = relationship(back_populates='pokemons',
                                                  secondary=pokedex)
  def __repr__(self):
    return f'<Pokemon: {self.name}>'
  

def add_all_types(user: User):
  grass = PokemonType(name='Grass', user=user)
  ground = PokemonType(name='Ground', user=user)
  fire = PokemonType(name='Fire', user=user)
  flying = PokemonType(name='Flying', user=user)
  water = PokemonType(name='Water', user=user)
  fighting = PokemonType(name='Fighting', user=user)
  normal = PokemonType(name='Normal', user=user)
  bug = PokemonType(name='Bug', user=user)
  steel = PokemonType(name='Steel', user=user)
  psychic = PokemonType(name='Psychic', user=user)
  ghost = PokemonType(name='Ghost', user=user)
  dark = PokemonType(name='Dark', user=user)
  ice = PokemonType(name='Ice', user=user)
  fairy = PokemonType(name='Fairy', user=user)
  dragon = PokemonType(name='Dragon', user=user)
  poison = PokemonType(name='Poison', user=user)
  electric = PokemonType(name='Electric', user=user)
  rock = PokemonType(name='Rock', user=user)

  db.session.add_all([
    grass, ground, fire, flying, water, fighting,
    normal, bug, steel, psychic, ghost, dark,
    ice, fairy, dragon, poison, electric, rock
  ])

  db.session.commit()
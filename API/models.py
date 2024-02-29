from sqlalchemy.orm import Session
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    DateTime,
    Sequence,
    event,
)
from database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from fastapi.encoders import jsonable_encoder


class Project(Base):
    __tablename__ = "project"
    id = Column(
        Integer,
        Sequence("project_id", metadata=Base.metadata, start=1, minvalue=1),
        primary_key=True,
    )

    name = Column(String, nullable=False)
    number_of_registrations = Column(Integer, nullable=False)
    number_of_participants = Column(Integer, nullable=False)
    sale_type = Column(String, nullable=False, default="ido")
    percent_raised = Column(Float, nullable=False)
    
    round_sale_id = Column(Integer, ForeignKey("round.id"), nullable=False)
    round_sale = relationship("Round", foreign_keys=[round_sale_id], lazy="joined")
    
    round_registration_id = Column(Integer, ForeignKey("round.id"))
    round_registration = relationship("Round", foreign_keys=[round_registration_id], lazy="joined")
    
    round_staking_id = Column(Integer, ForeignKey("round.id"))
    round_staking = relationship("Round", foreign_keys=[round_staking_id], lazy="joined")
    
    round_validation_id = Column(Integer, ForeignKey("round.id"))
    round_validation = relationship("Round", foreign_keys=[round_validation_id], lazy="joined")
    
    round_publicsale_id = Column(Integer, ForeignKey("round.id"))
    round_publicsale = relationship("Round", foreign_keys=[round_publicsale_id], lazy="joined")
    
    round_privatesale_id = Column(Integer, ForeignKey("round.id"))
    round_privatesale = relationship("Round", foreign_keys=[round_privatesale_id], lazy="joined")

    target_raised = Column(Integer, nullable=False)
    total_tokens_sold = Column(Float, nullable=False)
    total_raised = Column(Integer, nullable=False)
    state = Column(String, nullable=False)
    explanation_text = Column(String, nullable=False)
    website_url = Column(String, nullable=False)
    withdraw_all = Column(Boolean, nullable=False)
    staking_idle_time = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_staking_idle = Column(Boolean, nullable=False)
    is_airdrop = Column(Boolean, nullable=False)

    image_id = Column(Integer, ForeignKey("image.id"))
    social_id = Column(Integer, ForeignKey("social.id"))
    token_id = Column(Integer, ForeignKey("token.id"), nullable=False)

    is_active = Column(String, nullable=False)
    status = Column(Boolean, default = True)
    cuser = Column(Integer, ForeignKey("user.id"))
    cdate = Column(DateTime(timezone = True), server_default=func.now())
    uuser = Column(Integer, ForeignKey("user.id"))
    udate = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    image = relationship("ProjectImage", back_populates=("project"))
    social = relationship("Social", back_populates=("project"), lazy="joined")
    token = relationship("Token", back_populates=("project"), lazy="joined")


class Round(Base):
    __tablename__ = "round"
    id = Column(
        Integer,
        Sequence("round_id", metadata=Base.metadata, start=1, minvalue=1),
        primary_key=True,
    )

    round_type = Column(String, nullable=False)
    description = Column(String, default=None)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), default=None)
    # project = relationship("Project")

    status = Column(Boolean, default=True)
    cuser = Column(Integer, ForeignKey("user.id"))
    cdate = Column(DateTime(timezone=True), server_default=func.now())
    uuser = Column(Integer, ForeignKey("user.id"))
    udate = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Social(Base):
    __tablename__ = "social"
    id = Column(
        Integer,
        Sequence("social_id", metadata=Base.metadata, start=1, minvalue=1),
        primary_key=True,
    )

    twitter = Column(String, default=None)
    discord = Column(String, default=None)
    telegram = Column(String, default=None)

    status = Column(Boolean, default=True)
    cuser = Column(Integer, ForeignKey("user.id"))
    cdate = Column(DateTime(timezone=True), server_default=func.now())
    uuser = Column(Integer, ForeignKey("user.id"))
    udate = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project = relationship("Project", back_populates="social")


class Token(Base):
    __tablename__ = "token"
    id = Column(
        Integer,
        Sequence("token_id", metadata=Base.metadata, start=1, minvalue=1),
        primary_key=True,
    )

    name = Column(String, default=None)
    symbol = Column(String, default=None)
    decimals = Column(Integer, default=None)
    address = Column(String, default=None)
    owner_address = Column(String, default=None)
    total_supply = Column(Integer, default=None)
    price_in_usd = Column(Float, default=None)
    price_in_uno = Column(Float, default=None)
    distribution = Column(Integer, default=None)
    # total_raise = Column(Float, default=None)
    current_price = Column(Float, default=None)
    all_time_high = Column(Float, default=None)

    presale_contract_id = Column(Integer, ForeignKey("presale.id"))
    staking_contract_id = Column(Integer, ForeignKey("staking.id"))

    status = Column(Boolean, default=True)
    cuser = Column(Integer, ForeignKey("user.id"))
    cdate = Column(DateTime(timezone=True), server_default=func.now())
    uuser = Column(Integer, ForeignKey("user.id"))
    udate = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    presale_contract = relationship("Presale", back_populates=("token"))
    staking_contract = relationship("Staking", back_populates=("token"))
    project = relationship("Project", back_populates="token")


class Presale(Base):
    __tablename__ = "presale"
    id = Column(
        Integer,
        Sequence("presale_id", metadata=Base.metadata, start=1, minvalue=1),
        primary_key=True,
    )

    contract_address = Column(String, default=None)
    contract_owner_address = Column(String, default=None)

    status = Column(Boolean, default=True)
    cuser = Column(Integer, ForeignKey("user.id"))
    cdate = Column(DateTime(timezone=True), server_default=func.now())
    uuser = Column(Integer, ForeignKey("user.id"))
    udate = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    token = relationship("Token", back_populates="presale_contract")


class Staking(Base):
    __tablename__ = "staking"
    id = Column(
        Integer,
        Sequence("staking_id", metadata=Base.metadata, start=1, minvalue=1),
        primary_key=True,
    )

    contract_address = Column(String, default=None)
    contract_owner_address = Column(String, default=None)
    reward_token_address = Column(String, default=None)
    reward_token_owner_address = Column(String, default=None)

    status = Column(Boolean, default=True)
    cuser = Column(Integer, ForeignKey("user.id"))
    cdate = Column(DateTime(timezone=True), server_default=func.now())
    uuser = Column(Integer, ForeignKey("user.id"))
    udate = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    token = relationship("Token", back_populates="staking_contract")


class User(Base):
    __tablename__ = "user"
    id = Column(
        Integer,
        Sequence(
            "user_id", metadata=Base.metadata, start=100000000, minvalue=100000000
        ),
        primary_key=True,
    )
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(String, default="False")
    is_superuser = Column(Boolean, default=False)
    kyc_status = Column(Boolean, default=False)
    kyc_reason = Column(String)


class ProjectImage(Base):
    __tablename__ = "image"
    id = Column(
        Integer,
        Sequence(
            "image_id",
            metadata=Base.metadata,
            start=1,
            minvalue=1,
        ),
        primary_key=True,
    )
    image = Column(LargeBinary, default=None)
    logo = Column(LargeBinary, default=None)
    project = relationship("Project", back_populates="image")


class Token_log(Base):
    __tablename__ = "token_log"
    log_id = Column(Integer, primary_key=True, index=True)
    id = Column(Integer)
    
    name = Column(String, default=None)
    symbol = Column(String, default=None)
    decimals = Column(Integer, default=None)
    address = Column(String, default=None)
    owner_address = Column(String, default=None)
    total_supply = Column(Integer, default=None)
    price_in_usd = Column(Float, default=None)
    price_in_uno = Column(Float, default=None)
    distribution = Column(Integer, default=None)
    # total_raise = Column(Float, default=None)
    current_price = Column(Float, default=None)
    all_time_high = Column(Float, default=None)

    presale_contract_id = Column(Integer, ForeignKey("presale.id"))
    staking_contract_id = Column(Integer, ForeignKey("staking.id"))

    status = Column(Boolean, default=True)
    cuser = Column(Integer, ForeignKey("user.id"))
    cdate = Column(DateTime(timezone=True), server_default=func.now())
    uuser = Column(Integer, ForeignKey("user.id"))
    udate = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    action = Column(String, default=None)

class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(
        Integer,
        Sequence("transaction_id", metadata=Base.metadata, start=1, minvalue=1),
        primary_key=True,
    )
    project_id = Column(Integer)
    token_count = Column(Integer)
    user_public_address = Column(String)
    token_address = Column(String)
    transaction_time = Column(DateTime)
    transaction_status = Column(Boolean)
    status = Column(Boolean, default=True)
    cuser = Column(Integer, ForeignKey("user.id"))
    cdate = Column(DateTime(timezone=True), server_default=func.now())
    uuser = Column(Integer, ForeignKey("user.id"))
    udate = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    action = Column(String, default=None)


@event.listens_for(Token, "after_insert")
def receive_after_insert(mapper, connection, target):
    tbl = Token_log.__table__
    json_insert_audit = jsonable_encoder(target)
    json_insert_audit["action"] = "insert"
    connection.execute(tbl.insert().values(json_insert_audit))


@event.listens_for(Token, "after_update")
def receive_after_update(mapper, connection, target):
    tbl = Token_log.__table__
    json_insert_audit = jsonable_encoder(target)
    json_insert_audit["action"] = "update"
    connection.execute(tbl.insert().values(json_insert_audit))

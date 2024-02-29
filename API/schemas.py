from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr

class ProjectStatusType(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    INCOMING = "incoming"
    PAUSED = "paused"

class SaleType(str, Enum):
    IDO = "ido"
    ICO = "ico"


class RoundType(str, Enum):
    SALE = "sale"
    REGISTRATION = "registration"
    STAKING = "staking"
    VALIDATION = "validation"
    PUBLICSALE = "publicsale"
    PRIVATESALE = "privatesale"


class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = None
    number_of_registrations: Optional[int] = None
    number_of_participants: Optional[int] = None
    sale_type: Optional[SaleType] = None
    percent_raised: Optional[float] = None
    target_raised: Optional[int] = None
    total_tokens_sold: Optional[float] = None
    total_raised: Optional[int] = None
    state: Optional[str] = None
    explanation_text: Optional[str] = None
    website_url: Optional[str] = None
    withdraw_all: Optional[bool] = None
    staking_idle_time: Optional[datetime] = None
    is_staking_idle: Optional[bool] = None
    is_airdrop: Optional[bool] = None
    social_id: Optional[int] = None
    is_active: Optional[ProjectStatusType] = None

class TokenUpdateSchema(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    decimals: Optional[int] = None
    address: Optional[str] = None
    owner_address: Optional[str] = None
    total_supply: Optional[int] = None
    price_in_usd: Optional[float] = None
    price_in_uno: Optional[float] = None
    distribution: Optional[int] = None
    # total_raise: Optional[float] = None
    current_price: Optional[float] = None
    all_time_high: Optional[float] = None
    
    presale_contract_id: Optional[int] = None
    staking_contract_id: Optional[int] = None


class PresaleCreateSchema(BaseModel):
    contract_address: str
    contract_owner_address: str


class PresaleUpdateSchema(BaseModel):
    contract_address: Optional[str] = None
    contract_owner_address: Optional[str] = None


class StakingCreateSchema(BaseModel):
    contract_address: str
    contract_owner_address: str
    reward_token_address: str
    reward_token_owner_address: str


class StakingUpdateSchema(BaseModel):
    contract_address: Optional[str] = None
    contract_owner_address: Optional[str] = None
    reward_token_address: Optional[str] = None
    reward_token_owner_address: Optional[str] = None


class TokenCreateSchema(BaseModel):
    name: str
    symbol: str
    decimals: int
    address: str
    owner_address: str
    total_supply: int
    price_in_usd: float
    price_in_uno: float
    distribution: int
    # total_raise: float
    current_price: float
    all_time_high: float
    staking_contract: Optional[StakingCreateSchema] = None
    presale_contract: Optional[PresaleCreateSchema] = None


class SocialSchema(BaseModel):
    twitter: Optional[str] = None
    discord: Optional[str] = None
    telegram: Optional[str] = None


class RoundCreateSchema(BaseModel):
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None


class RoundUpdateSchema(BaseModel):
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectCreateSchema(BaseModel):
    name: str
    number_of_registrations: int
    number_of_participants: int
    sale_type: SaleType
    percent_raised: float
    round_sale: RoundCreateSchema
    target_raised: int
    total_tokens_sold: float
    total_raised: int
    state: str
    explanation_text: str
    website_url: str
    withdraw_all: bool
    staking_idle_time: datetime
    is_staking_idle: bool
    is_airdrop: bool

    # TODO: image
    token: TokenCreateSchema
    social: Optional[SocialSchema] = None
class TransactionCreateSchema(BaseModel):
    project_id: int
    token_count: int
    user_public_address: str
    token_address: str
    transaction_time: datetime
    transaction_status: bool

class BscSchema(BaseModel):
    module: str
    action: str
    address: str
    params: Optional[dict] = None


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[str] = "False"
    is_superuser: bool = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class UserKYCUpdate(BaseModel):
    kyc_status: bool
    kyc_reason: Optional[str] = None


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class Msg(BaseModel):
    msg: str


class PassToken(BaseModel):
    token: str


class Image(BaseModel):
    image: bytes
    logo: bytes


class UnopadToken(BaseModel):
    token_address: str

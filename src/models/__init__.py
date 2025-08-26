# python-training/lessons/points_system/src/models/__init__.py

"""
This __init__.py file serves two purposes:
1. It makes the 'models' directory a Python package.
2. It imports all of the models, making them easily accessible from the top-level
   package. This is also crucial for Alembic's autogenerate feature to detect
   all the tables.

Example usage elsewhere in the project:
from src.models import User, Account, Transaction, UserPoint
"""

from .token import Token
from .partner import Partner
from .partner_pool import PartnerPool
from .partner_uniswapv3_lp import PartnerUniswapV3LP
from .partner_uniswapv3_tick import PartnerUniswapV3Tick
# from .partner_uniswapv3_event import PartnerUniswapV3Event
from .partner_pool_uniswapv3 import PartnerPoolUniswapV3
from .partner_user_position import PartnerUserPosition
from .partner_protocol_event import PartnerProtocolEvent
from .points_campaign import PointsCampaign
from .points_point_type import PointsPointType
from .points_user_campaign_points import PointsUserCampaignPoints
from .points_user_point import PointsUserPoint
from .points_user_point_history import PointsUserPointHistory
from .points_partner_snapshot import PointsPartnerSnapshot
from .vaults import Vault
from .vaults_user_position_history import VaultsUserPositionHistory, PositionHistoryType
from .vaults_user_position import VaultsUserPosition

__all__ = [
    "Partner",
    "PartnerPool",
    "PartnerPoolUniswapV3",
    "Token",
    "PartnerUniswapV3LP",
    "PartnerUniswapV3Tick",
    # "PartnerUniswapV3Event",
    "PartnerUserPosition",
    "PartnerProtocolEvent",
    "PointsCampaign",
    "PointsPointType",
    "PointsUserCampaignPoints",
    "PointsUserPoint",
    "PointsUserPointHistory",
    "PointsPartnerSnapshot",
    "Vault",
    "VaultsUserPositionHistory",
    "PositionHistoryType",
    "VaultsUserPosition",
]

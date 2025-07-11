"""
Initialize sample inventory data on service startup
Path: services/inventory-service/src/data/init_inventory.py
"""
import logging
from typing import List
from datetime import datetime
from decimal import Decimal

from common.dao.asset_dao import AssetDAO
from common.entities.asset import AssetCreate
from common.database.dynamodb_connection import dynamodb_manager

logger = logging.getLogger(__name__)


# Sample inventory data for learning/demo purposes
SAMPLE_ASSETS = [
    # Major Cryptocurrencies
    {
        "asset_id": "BTC",
        "name": "Bitcoin",
        "description": "Bitcoin is a decentralized digital currency that can be transferred on the peer-to-peer bitcoin network without the need for intermediaries.",
        "category": "major",
        "amount": Decimal("1000.0"),
        "price_usd": Decimal("45000.00")
    },
    {
        "asset_id": "ETH",
        "name": "Ethereum",
        "description": "Ethereum is a decentralized, open-source blockchain with smart contract functionality.",
        "category": "major",
        "amount": Decimal("5000.0"),
        "price_usd": Decimal("3000.00")
    },
    {
        "asset_id": "BNB",
        "name": "Binance Coin",
        "description": "Binance Coin is the cryptocurrency coin that powers the Binance ecosystem.",
        "category": "major",
        "amount": Decimal("2000.0"),
        "price_usd": Decimal("350.00")
    },

    # Altcoins
    {
        "asset_id": "ADA",
        "name": "Cardano",
        "description": "Cardano is a proof-of-stake blockchain platform founded on peer-reviewed research.",
        "category": "altcoin",
        "amount": Decimal("10000.0"),
        "price_usd": Decimal("0.50")
    },
    {
        "asset_id": "DOT",
        "name": "Polkadot",
        "description": "Polkadot is a multi-chain interchange and translation architecture which enables customized side-chains.",
        "category": "altcoin",
        "amount": Decimal("8000.0"),
        "price_usd": Decimal("7.25")
    },
    {
        "asset_id": "LINK",
        "name": "Chainlink",
        "description": "Chainlink is a decentralized oracle network that bridges the gap between smart contracts and real-world data.",
        "category": "altcoin",
        "amount": Decimal("15000.0"),
        "price_usd": Decimal("15.50")
    },
    {
        "asset_id": "MATIC",
        "name": "Polygon",
        "description": "Polygon is a decentralized platform that provides tools for developers to build scalable dApps.",
        "category": "altcoin",
        "amount": Decimal("25000.0"),
        "price_usd": Decimal("1.20")
    },
    {
        "asset_id": "AVAX",
        "name": "Avalanche",
        "description": "Avalanche is a layer one blockchain that functions as a platform for decentralized applications.",
        "category": "altcoin",
        "amount": Decimal("3000.0"),
        "price_usd": Decimal("35.00")
    },

    # Stablecoins
    {
        "asset_id": "USDT",
        "name": "Tether",
        "description": "Tether is a blockchain-based cryptocurrency whose tokens are backed by an equivalent amount of traditional fiat currencies.",
        "category": "stablecoin",
        "amount": Decimal("100000.0"),
        "price_usd": Decimal("1.00")
    },
    {
        "asset_id": "USDC",
        "name": "USD Coin",
        "description": "USD Coin is a digital stablecoin that is pegged to the United States dollar.",
        "category": "stablecoin",
        "amount": Decimal("75000.0"),
        "price_usd": Decimal("1.00")
    },
    {
        "asset_id": "DAI",
        "name": "Dai",
        "description": "Dai is a stablecoin cryptocurrency which aims to keep its value as close to one United States dollar.",
        "category": "stablecoin",
        "amount": Decimal("50000.0"),
        "price_usd": Decimal("1.00")
    },

    # Inactive asset for testing
    {
        "asset_id": "DEAD",
        "name": "Dead Coin",
        "description": "An inactive cryptocurrency for testing purposes.",
        "category": "altcoin",
        "amount": Decimal("0.0"),
        "price_usd": Decimal("0.00")  # This will make it inactive automatically
    }
]


async def check_if_data_exists() -> bool:
    """Check if inventory data already exists in the database"""
    try:
        async with dynamodb_manager.get_connection() as db_connection:
            asset_dao = AssetDAO(db_connection)

            # Check if any assets exist
            existing_assets = await asset_dao.get_all_assets(active_only=False)

            if existing_assets:
                logger.info(f"Found {len(existing_assets)} existing assets in database")
                return True
            else:
                logger.info("No existing assets found in database")
                return False

    except Exception as e:
        logger.error(f"Error checking existing data: {e}")
        return False


async def create_sample_assets() -> int:
    """Create sample assets in the database"""
    created_count = 0

    try:
        async with dynamodb_manager.get_connection() as db_connection:
            asset_dao = AssetDAO(db_connection)

            for asset_data in SAMPLE_ASSETS:
                try:
                    # Create AssetCreate model
                    asset_create = AssetCreate(
                        asset_id=asset_data["asset_id"],
                        name=asset_data["name"],
                        description=asset_data["description"],
                        category=asset_data["category"],
                        amount=asset_data["amount"],
                        price_usd=asset_data["price_usd"]
                    )

                    # Check if asset already exists
                    existing_asset = await asset_dao.get_asset_by_id(asset_create.asset_id)
                    if existing_asset:
                        logger.info(f"Asset {asset_create.asset_id} already exists, skipping...")
                        continue

                    # Create the asset
                    created_asset = await asset_dao.create_asset(asset_create)
                    logger.info(f"Created asset: {created_asset.asset_id} - {created_asset.name}")
                    created_count += 1

                except Exception as e:
                    logger.error(f"Failed to create asset {asset_data['asset_id']}: {e}")
                    continue

    except Exception as e:
        logger.error(f"Error creating sample assets: {e}")
        raise

    return created_count


async def initialize_inventory_data(force_recreate: bool = False) -> dict:
    """
    Initialize inventory data on service startup

    Args:
        force_recreate: If True, will recreate data even if it exists

    Returns:
        Dictionary with initialization results
    """
    logger.info("🚀 Starting inventory data initialization...")

    try:
        # Check if data already exists
        data_exists = await check_if_data_exists()

        if data_exists and not force_recreate:
            logger.info("✅ Inventory data already exists, skipping initialization")
            return {
                "status": "skipped",
                "reason": "data_already_exists",
                "message": "Inventory data already populated"
            }

        if force_recreate:
            logger.warning("⚠️ Force recreate flag set - this would require clearing existing data")
            logger.info("For this demo, we'll just add new assets if they don't exist")

        # Create sample assets
        logger.info("📦 Creating sample inventory assets...")
        created_count = await create_sample_assets()

        if created_count > 0:
            logger.info(f"✅ Successfully initialized {created_count} assets")
            return {
                "status": "success",
                "assets_created": created_count,
                "message": f"Successfully created {created_count} sample assets"
            }
        else:
            logger.info("ℹ️ No new assets were created (all already exist)")
            return {
                "status": "no_changes",
                "assets_created": 0,
                "message": "All sample assets already exist"
            }

    except Exception as e:
        logger.error(f"❌ Failed to initialize inventory data: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to initialize inventory data"
        }


async def get_inventory_summary() -> dict:
    """Get a summary of current inventory for logging/debugging"""
    try:
        async with dynamodb_manager.get_connection() as db_connection:
            asset_dao = AssetDAO(db_connection)

            # Get asset statistics
            stats = await asset_dao.get_asset_stats()

            return {
                "total_assets": stats["total_assets"],
                "active_assets": stats["active_assets"],
                "inactive_assets": stats["inactive_assets"],
                "categories": stats["assets_by_category"],
                "last_updated": stats["last_updated"]
            }

    except Exception as e:
        logger.error(f"Error getting inventory summary: {e}")
        return {
            "error": str(e)
        }


# Convenience function for startup
async def startup_inventory_initialization():
    """Convenience function to call during FastAPI startup event"""
    logger.info("🎯 Inventory Service - Data Initialization")

    try:
        # Initialize data
        result = await initialize_inventory_data()

        # Log summary
        summary = await get_inventory_summary()

        logger.info("📊 Current Inventory Summary:")
        if "error" not in summary:
            logger.info(f"  Total Assets: {summary.get('total_assets', 'unknown')}")
            logger.info(f"  Active Assets: {summary.get('active_assets', 'unknown')}")
            logger.info(f"  Categories: {summary.get('categories', {})}")
        else:
            logger.warning(f"  Could not get summary: {summary['error']}")

        logger.info(f"🏁 Initialization Result: {result['status']} - {result['message']}")

        return result

    except Exception as e:
        logger.error(f"❌ Startup initialization failed: {e}")
        raise
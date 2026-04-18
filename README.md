# 🚗 Customs Calculator Bot
Telegram bot for calculating customs duties for vehicles imported from China to Kazakhstan.

## Features
- Step-by-step data input with inline keyboards
- Real-time currency rates from morning briefing
- Multiple tariff plans (free, pay-per-use, packages, subscription)
- Kaspi API integration for payments
- User history and calculation storage

## Business Model
### Tariffs:
1. **Free:** 3 calculations/month, electric vehicles only
2. **Pay-per-use:** 299 ₸/calculation, all vehicle types
3. **Packages:** 500/1,000/2,000 ₸ (discount up to 44%)
4. **Subscription:** 1,990 ₸/month, unlimited calculations
5. **Corporate:** From 5,000 ₸/month, branding, API access

## Technical Stack
- **Bot:** Python + python-telegram-bot
- **Database:** PostgreSQL
- **Payments:** Kaspi API + Stripe (backup)
- **Hosting:** VPS (TimeWeb, 1,500 ₸/month)
- **Domain:** customs.kz (1,800 ₸/year)

## Project Structure
```
customs_calculator_project/
├── src/
│   ├── bot/           # Telegram bot handlers
│   ├── calculator/    # Customs duty calculation logic
│   ├── database/      # PostgreSQL models and migrations
│   ├── payment/       # Kaspi API integration
│   └── utils/         # Helper functions
├── config/            # Configuration files
├── tests/             # Unit and integration tests
├── docs/              # Documentation
└── deployment/        # Deployment scripts
```

## Development Plan
### Day 1: Infrastructure (18-19 April 2026)
- [ ] Register bot via @BotFather
- [ ] Rent VPS on TimeWeb
- [ ] Register domain customs.kz
- [ ] Create GitHub repository

### Day 2-3: Bot Development (20-21 April 2026)
- [ ] Adapt existing calculator
- [ ] Implement step-by-step input with inline keyboards
- [ ] Database setup and migrations

### Day 4: Payment Integration (22 April 2026)
- [ ] Kaspi Merchant registration
- [ ] Kaspi API integration
- [ ] Payment verification system

### Day 5: Testing (23 April 2026)
- [ ] Full cycle testing
- [ ] Payment testing
- [ ] Bug fixes

### Day 6: Deployment (24 April 2026)
- [ ] Deploy to VPS
- [ ] Configure webhook
- [ ] Documentation

### Day 7: Launch MVP (25 April 2026)
- [ ] Final testing
- [ ] Launch for first users
- [ ] Collect feedback

## Installation
```bash
git clone https://github.com/[username]/customs-calculator-bot.git
cd customs-calculator-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration
1. Copy `.env.example` to `.env`
2. Set your Telegram bot token
3. Configure database connection
4. Set Kaspi API credentials

## License
MIT

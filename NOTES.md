# Development Notes

## Transformation Logic

### MRR Calculation
- Free plan: $0/month
- Pro plan: $29/month  
- Enterprise plan: $99/month

### Event Types
- **signup**: New customer subscription
- **upgrade**: Moving to higher plan (increases MRR)
- **downgrade**: Moving to lower plan (decreases MRR)
- **cancel**: Subscription cancelled (MRR becomes $0)

### Data Quality Rules
1. No duplicate user_ids or subscription_ids
2. All subscriptions must have valid user_id
3. Event dates should not be in the future
4. Plan IDs must be: free, pro, or enterprise
5. Event types must be: signup, upgrade, downgrade, cancel

### Date Key Format
- YYYYMMDD as integer
- Example: 2024-01-15 → 20240115
- Makes joins with date dimension easier

## Sample Calculations

### Current MRR
Sum of all non-cancelled subscriptions:
- If user has multiple events, use the latest plan

### Churn Rate
- Cancelled subscriptions / Total active subscriptions
- Calculated monthly

### Customer Lifetime Value (LTV)
- Average MRR per customer × Average customer lifetime
- Simplified: Total revenue / Total customers
#
# Filter filtered.csv file to hold only web_nav, purchase, and cart events
# split into separate file by user and write to users directory
#
import os
import time
import pandas as pd

df = pd.read_csv('filtered.csv')

# Filter for specific event types
filtered_df = df[df['event'].isin(['web_navigation', 'purchase', 'cart'])]

# write filtered file to csv
filtered_df.to_csv('purchase_cart_webnav_only.csv', index=False)

exp_device_id = filtered_df['properties_$device_id'].unique()

# exp_device_id.to_csv('unique_device_ids.csv', index=False)

for device_id in exp_device_id:
    matching_rows = filtered_df[filtered_df['properties_$device_id'] == device_id]
    filename = f"users/{device_id}.csv"
    matching_rows.to_csv(filename, index=False)
    print(f"Saved {device_id} to {filename}")


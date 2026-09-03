-- Top 10 corridors by ridership
SELECT corridorName, COUNT(*) as trip_count
FROM trips
GROUP BY corridorName
ORDER BY trip_count DESC
LIMIT 10;

-- Hourly ridership (weekday vs weekend)
SELECT 
    strftime('%H', tapInTime) as hour,
    SUM(CASE WHEN is_weekend = 0 THEN 1 ELSE 0 END) as weekday_trips,
    SUM(CASE WHEN is_weekend = 1 THEN 1 ELSE 0 END) as weekend_trips
FROM trips
GROUP BY hour
ORDER BY hour;

-- Weekday vs weekend total trips
SELECT 
    CASE WHEN is_weekend = 0 THEN 'Weekday' ELSE 'Weekend' END as day_type,
    COUNT(*) as total_trips
FROM trips
GROUP BY is_weekend;

-- Average trip duration by corridor (top 10 longest)
SELECT 
    corridorName,
    AVG(trip_duration_min) as avg_duration_min
FROM trips
GROUP BY corridorName
ORDER BY avg_duration_min DESC
LIMIT 10;

-- Corridor ranking by average duration (using window function)
SELECT 
    corridorName,
    AVG(trip_duration_min) as avg_duration_min,
    RANK() OVER (ORDER BY AVG(trip_duration_min) DESC) as duration_rank
FROM trips
GROUP BY corridorName
ORDER BY duration_rank
LIMIT 10;

-- Peak-hour analysis: hour with most trips per day type
WITH hourly AS (
    SELECT 
        strftime('%H', tapInTime) as hour,
        CASE WHEN is_weekend = 0 THEN 'Weekday' ELSE 'Weekend' END as day_type,
        COUNT(*) as trips
    FROM trips
    GROUP BY hour, is_weekend
),
ranked AS (
    SELECT 
        hour,
        day_type,
        trips,
        RANK() OVER (PARTITION BY day_type ORDER BY trips DESC) as rank
    FROM hourly
)
SELECT hour, day_type, trips
FROM ranked
WHERE rank = 1;
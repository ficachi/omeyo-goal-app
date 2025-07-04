-- Dummy Footprints Data for User 1 - Personal Growth & Health
-- Insert 5 footprints related to personal development, health, and fitness

-- Personal Growth & Health Footprints
INSERT INTO footprints (user_id, action, path_name, path_color, due_time, is_completed, priority) VALUES
(1, 'Drink 8 glasses of water today', 'Health & Hydration', 'bg-blue-100 text-blue-800', CURRENT_DATE, 0, 1),
(1, 'Do 20 push-ups', 'Physical Fitness', 'bg-green-100 text-green-800', CURRENT_DATE, 0, 2),
(1, 'Go for a 30-minute walk', 'Cardio Health', 'bg-purple-100 text-purple-800', CURRENT_DATE, 0, 1),
(1, 'Eat a healthy breakfast', 'Nutrition', 'bg-orange-100 text-orange-800', CURRENT_DATE + INTERVAL '1 day', 0, 1),
(1, 'Stretch for 10 minutes', 'Flexibility', 'bg-pink-100 text-pink-800', CURRENT_DATE, 1, 2);

-- Display the inserted data
SELECT 
    f.id,
    f.user_id,
    u.name as user_name,
    f.action,
    f.path_name,
    f.path_color,
    f.due_time,
    CASE WHEN f.is_completed = 1 THEN 'Completed' ELSE 'Pending' END as status,
    f.priority
FROM footprints f
JOIN users u ON f.user_id = u.id
WHERE f.user_id = 1
ORDER BY f.priority, f.due_time; 
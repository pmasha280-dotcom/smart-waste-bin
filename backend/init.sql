-- Создание пользователей (пароль для admin и worker: "admin123")
INSERT INTO users (username, email, hashed_password, role, is_active) VALUES 
('admin', 'admin@smartbins.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyYfY7YBhQbRji', 'admin', true),
('worker', 'worker@smartbins.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyYfY7YBhQbRji', 'worker', true),
('demo_user', 'demo@smartbins.com', NULL, 'guest', true);

-- Демо-данные будут добавлены через API эндпоинт /simulation/initialize-data
-- Это позволяет избежать дублирования при перезапуске
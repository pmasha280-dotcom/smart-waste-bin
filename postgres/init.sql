-- Создание пользователей (пароль для admin и worker: "admin123")
INSERT INTO users (username, email, hashed_password, role, is_active) VALUES 
('admin', 'admin@smartbins.com', '\\\/LewKyYfY7YBhQbRji', 'admin', true),
('worker', 'worker@smartbins.com', '\\\/LewKyYfY7YBhQbRji', 'worker', true),
('demo_user', 'demo@smartbins.com', NULL, 'guest', true)
ON CONFLICT (username) DO NOTHING;

-- Создание этажей (если не существуют)
INSERT INTO floors (name, level) VALUES 
('Первый этаж', 1),
('Второй этаж', 2),
('Третий этаж', 3)
ON CONFLICT (level) DO NOTHING;

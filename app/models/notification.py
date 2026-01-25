

class Notification:
    def __init__(self, notif_id, user_id, title, message, notif_type, is_public, is_read, date_created):
        self.notif_id = notif_id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.notif_type = notif_type
        self.is_public = is_public
        self.is_read = is_read
        self.date_created = date_created

    @staticmethod
    def get_all_public_notifications(db):
        """Lấy tất cả thông báo công khai (không cần đăng nhập)"""
        query = "SELECT * FROM notifications WHERE is_public = 1 ORDER BY created_at DESC"
        rows = db.execute_query(query)
        return [Notification(
            row['notification_id'], 
            row['user_id'],
            row['title'], 
            row['message'],
            row['type'],
            row['is_public'],
            row['is_read'],
            row['created_at']
        ) for row in rows]
    
    @staticmethod
    def get_user_notifications(user_id, db):
        """Lấy thông báo cá nhân của user + public notifications"""
        query = """
            SELECT * FROM notifications 
            WHERE (user_id = ? AND is_public = 0) OR is_public = 1
            ORDER BY created_at DESC
        """
        rows = db.execute_query(query, (user_id,))
        return [Notification(
            row['notification_id'], 
            row['user_id'],
            row['title'], 
            row['message'],
            row['type'],
            row['is_public'],
            row['is_read'],
            row['created_at']
        ) for row in rows]
    
    def get_detail(self):
        type_icon = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'success': '✅',
            'error': '❌'
        }
        icon = type_icon.get(self.notif_type, 'ℹ️')
        return f"{icon} {self.title}\nDate: {self.date_created}\n\n{self.message}"

    @staticmethod
    def view_notif(notifications):
        print("\n[PUBLIC ANNOUNCEMENTS]")
        if not notifications:
            print("No announcements available.")
            return
        
        print(f"Found {len(notifications)} announcement(s):\n")
        for idx, notif in enumerate(notifications, 1):
            type_icon = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'success': '✅',
                'error': '❌'
            }
            icon = type_icon.get(notif.notif_type, 'ℹ️')
            print(f"{idx}. {icon} {notif.title}")
            print(f"   {notif.date_created}")
            print(f"   {notif.message}\n")

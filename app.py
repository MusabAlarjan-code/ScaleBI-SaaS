import streamlit as st
import pandas as pd
import numpy as np
import io
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. البنية التحتية المتكاملة لقاعدة البيانات والتحقق (Database v3.0) ---
def init_db():
    conn = sqlite3.connect("scalebi_enterprise_v30.db")
    cursor = conn.cursor()
    
    # جدول المستخدمين المطور (يشمل حقول التراخيص والتواريخ وحالة الحساب)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT,
            license_key TEXT,
            store_name TEXT,
            sub_start TEXT,
            sub_end TEXT,
            role TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # جدول المفاتيح المصدرة من الأدمن (التي لم تفعل بعد أو تم حجزها)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_licenses (
            key TEXT PRIMARY KEY,
            duration_days INTEGER,
            is_used INTEGER DEFAULT 0,
            generated_at TEXT
        )
    ''')
    
    # جدول السجل التاريخي لحفظ لقطات التقارير وعزلها بالبريد الإلكتروني
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            report_date TEXT,
            revenue REAL,
            orders_count INTEGER,
            best_product TEXT
        )
    ''')
    
    # زرع حساب المدير (الأدمن) الافتراضي وتأمين كلمة المرور
    # الباسورد الافتراضي: admin123
    admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (email, password_hash, license_key, store_name, sub_start, sub_end, role)
        VALUES ('admin@scalebi.com', ?, 'MASTER-SYSTEM-KEY', 'منصة الإدارة العليا', '2026-01-01', '2030-01-01', 'admin')
    ''', (admin_hash,))
    
    # زرع بعض المفاتيح الجاهزة في النظام للتجربة والمعاينة
    cursor.execute("INSERT OR IGNORE INTO master_licenses VALUES ('SCALE-PRO-30DAYS', 30, 0, '2026-06-01')")
    cursor.execute("INSERT OR IGNORE INTO master_licenses VALUES ('SCALE-EXPERT-90DAYS', 90, 0, '2026-06-01')")
    
    conn.commit()
    conn.close()

init_db()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- إعدادات وتصميم المنصة ---
st.set_page_config(page_title="ScaleBI Enterprise v3.0", layout="wide")

# --- 2. المحرك الاستراتيجي المتكامل لذكاء الأعمال (SaaS Intelligence Core) ---
class ScaleBIIntelligenceCore:
    def __init__(self, df):
        self.df = df.copy() if df is not None else pd.DataFrame()
        self.initial_rows = len(self.df)
        
    def process_all_engines(self):
        if self.df.empty:
            return pd.DataFrame(), 100, {}, pd.DataFrame(), pd.DataFrame()
            
        # أ) نظام تنظيف وتوحيد البيانات المتطور
        missing_vals = self.df.isnull().sum().sum()
        duplicates = self.df.duplicated().sum()
        
        ecom_mapping = {
            'رقم الطلب': 'رقم_الطلب', 'رقم طلب': 'رقم_الطلب', 'Order ID': 'رقم_الطلب',
            'تاريخ الطلب': 'تاريخ_الطلب', 'تاريخ طلب': 'تاريخ_الطلب', 'Date': 'تاريخ_الطلب',
            'حالة الطلب': 'حالة_الطلب', 'حالة طلب': 'حالة_الطلب', 'Status': 'حالة_الطلب',
            'اسم المنتج': 'اسم_المنتج', 'المنتج': 'اسم_المنتج', 'Product Name': 'اسم_المنتج',
            'الكمية': 'الكمية', 'الكمية المباعة': 'الكمية', 'Quantity': 'الكمية',
            'سعر الوحدة': 'سعر_الوحدة', 'السعر': 'سعر_الوحدة', 'Price': 'سعر_الوحدة',
            'مدينة العميل': 'المدينة', 'المدينة': 'المدينة', 'City': 'المدينة',
            'إجمالي المنتج': 'إجمالي_المنتج', 'صافي المبيعات': 'إجمالي_المنتج',
            'بريد العميل': 'بريد_العميل', 'إيميل العميل': 'بريد_العميل', 'Customer Email': 'بريد_العميل'
        }
        self.df.rename(columns=ecom_mapping, inplace=True)
        
        # حماية الأعمدة الأساسية وتوليد الافتراضية عند النقص
        if 'الكمية' not in self.df.columns: self.df['الكمية'] = 1
        if 'سعر_الوحدة' not in self.df.columns: self.df['سعر_الوحدة'] = 0.0
        if 'حالة_الطلب' not in self.df.columns: self.df['حالة_الطلب'] = 'مكتمل'
        if 'بريد_العميل' not in self.df.columns:
            # توليد بريد وهمي للمعاينة إذا لم يوجد لضمان عمل محرك الـ RFM
            self.df['بريد_العميل'] = 'customer_' + np.random.randint(100, 150, size=len(self.df)).astype(str) + '@test.com'

        # عزل ومكافحة النزيف المالي من السجلات الفاشلة
        bleeding = ['ملغي', 'مسترجع', 'بانتظار الدفع', 'مرفوض', 'Canceled', 'Refunded']
        self.df = self.df[~self.df['حالة_الطلب'].astype(str).str.strip().isin(bleeding)]

        self.df['الكمية'] = pd.to_numeric(self.df['الكمية'], errors='coerce').fillna(1).abs()
        self.df['سعر_الوحدة'] = pd.to_numeric(self.df['سعر_الوحدة'], errors='coerce').fillna(0).abs()
        self.df['إجمالي_المبيعات'] = self.df['الكمية'] * self.df['سعر_الوحدة']
        
        if 'تاريخ_الطلب' in self.df.columns:
            self.df['تاريخ_الطلب'] = pd.to_datetime(self.df['تاريخ_الطلب'], errors='coerce')
        else:
            self.df['تاريخ_الطلب'] = pd.date_range(start="2026-05-01", periods=len(self.df), freq='H')
            
        self.df.drop_duplicates(inplace=True)
        
        # ميزان جودة البيانات الرياضي
        quality_score = 100
        if self.initial_rows > 0:
            quality_score -= int((missing_vals / (self.initial_rows * len(self.df.columns))) * 100 * 2)
            quality_score -= int((duplicates / self.initial_rows) * 100 * 3)
        quality_score = max(min(quality_score, 100), 20)
        
        # ب) محرك الـ KPIs ومؤشرات الذكاء التجاري الأساسية
        kpis = {}
        if 'اسم_المنتج' in self.df.columns:
            prod_perf = self.df.groupby('اسم_المنتج')['إجمالي_المبيعات'].sum()
            kpis['best_product'] = prod_perf.idxmax() if not prod_perf.empty else "N/A"
            kpis['worst_product'] = prod_perf.idxmin() if not prod_perf.empty else "N/A"
            
        if 'المدينة' in self.df.columns:
            city_perf = self.df.groupby('المدينة')['إجمالي_المبيعات'].sum()
            kpis['best_city'] = city_perf.idxmax() if not city_perf.empty else "N/A"
            kpis['worst_city'] = city_perf.idxmin() if not city_perf.empty else "N/A"

        # ج) محرك إدارة مخاطر ونفاد المخزون (Inventory Risk Engine)
        # نفترض جدلاً أن مخزون البداية الافتراضي الحالي لكل منتج في المستودع هو 150 قطعة لمراقبة النفاد
        inv_df = self.df.groupby('اسم_المنتج').agg(
            الكمية_المباعة=('الكمية', 'sum')
        ).reset_index()
        inv_df['المخزون_المتبقي_التقديري'] = 150 - inv_df['الكمية_المباعة']
        inv_df['المخزون_المتبقي_التقديري'] = inv_df['المخزون_المتبقي_التقديري'].clip(lower=0)
        inv_df['معدل_الطلب_اليومي'] = (inv_df['الكمية_المباعة'] / 30).round(2) # بافتراض شهر من البيانات
        inv_df['الأيام_المتبقية_قبل_النفاد'] = (inv_df['المخزون_المتبقي_التقديري'] / inv_df['معدل_الطلب_اليومي'].replace(0, 1)).round(1)
        
        # د) محرك تحليل وتصنيف العملاء المتقدم (RFM Analysis Engine)
        # Recency (الحداثة)، Frequency (التكرار)، Monetary (القيمة المالية)
        latest_date = self.df['تاريخ_الطلب'].max()
        rfm = self.df.groupby('بريد_العميل').agg({
            'تاريخ_الطلب': lambda x: (latest_date - x.max()).days,
            'رقم_الطلب': 'count',
            'إجمالي_المبيعات': 'sum'
        }).rename(columns={'تاريخ_الطلب': 'Recency', 'رقم_الطلب': 'Frequency', 'إجمالي_المبيعات': 'Monetary'})
        
        # تقسيم العملاء إلى 3 مجموعات بناءً على القيمة المالية والتكرار
        def segment_customer(row):
            if row['Monetary'] >= rfm['Monetary'].quantile(0.7):
                return '💎 عملاء ملوك (VIP)'
            elif row['Frequency'] >= rfm['Frequency'].median() and row['Recency'] <= 10:
                return '🔄 عملاء نشطين ومخلصين'
            else:
                return '⚠️ عملاء مهددين بالمغادرة'
                
        rfm['تصنيف_العميل'] = rfm.apply(segment_customer, axis=1)
        
        return self.df, quality_score, kpis, inv_df, rfm.reset_index()

    # محرك التنبؤ الإحصائي الرياضي المبسط (Linear Regression Predictive Engine)
    def run_predictive_forecasting(self):
        if 'تاريخ_الطلب' not in self.df.columns or self.df.empty:
            return pd.DataFrame()
        
        # تجميع المبيعات حسب التاريخ (اليومي)
        daily_sales = self.df.groupby(self.df['تاريخ_الطلب'].dt.date)['إجمالي_المبيعات'].sum().reset_index()
        daily_sales.columns = ['Date', 'Sales']
        
        if len(daily_sales) < 3:
            return pd.DataFrame() # بيانات غير كافية للتنبؤ الإحصائي
            
        # تحويل التواريخ إلى أرقام متسلسلة (مؤشر الوقت X) لتطبيق الانحدار الخطي
        X = np.arange(len(daily_sales)).reshape(-1, 1)
        y = daily_sales['Sales'].values
        
        # حساب معادلة خط الاتجاه يدوياً بدون مكتبات خارجية ثقيلة: y = mx + c
        n = len(X)
        X_mean = np.mean(X)
        y_mean = np.mean(y)
        
        slope = np.sum((X.flatten() - X_mean) * (y - y_mean)) / np.sum((X.flatten() - X_mean)**2)
        intercept = y_mean - slope * X_mean
        
        # التنبؤ بـ 7 أيام قادمة في المستقبل
        future_indices = np.arange(n, n + 7)
        future_predictions = (slope * future_indices + intercept).clip(lower=0)
        
        future_dates = [daily_sales['Date'].max() + timedelta(days=int(i)) for i in range(1, 8)]
        
        forecast_df = pd.DataFrame({
            'التاريخ المستقبلي': future_dates,
            'المبيعات المتوقعة (د.أ)': future_predictions.round(2)
        })
        return forecast_df

    def generate_heavy_mock_data(self):
        np.random.seed(101)
        size = 800
        dates = pd.date_range(start="2026-05-01", periods=size, freq='2h')
        products = ['عطر توباكو ملكي', 'ساعة كلاسيك ذكية', 'محفظة جلدية فاخرة', 'منظم مكتب خشبي']
        cities = ['الرياض', 'جدة', 'عمان', 'الدمام', 'الزرقاء']
        emails = ['user_01@gmail.com', 'user_02@yahoo.com', 'user_03@hotmail.com', 'user_04@gmail.com']
        
        df = pd.DataFrame({
            'رقم الطلب': np.random.randint(400000, 800000, size=size),
            'تاريخ الطلب': np.random.choice(dates, size=size),
            'حالة الطلب': np.random.choice(['مكتمل', 'تم الشحن', 'ملغي'], size=size, p=[0.80, 0.15, 0.05]),
            'اسم المنتج': np.random.choice(products, size=size),
            'الكمية': np.random.choice([1, 2, 3], size=size, p=[0.85, 0.10, 0.05]),
            'سعر الوحدة': np.random.choice([290, 450, 95, 130], size=size),
            'مدينة العميل': np.random.choice(cities, size=size),
            'بريد العميل': np.random.choice(emails, size=size)
        })
        return df

# --- 3. نظام الجلسات والتحقق من حالة الاشتراك (Session & Auth Guards) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'role' not in st.session_state:
    st.session_state.role = "user"
if 'store_name' not in st.session_state:
    st.session_state.store_name = ""
if 'sub_end_date' not in st.session_state:
    st.session_state.sub_end_date = ""
if 'file_data' not in st.session_state:
    st.session_state.file_data = None

# --- بوابات الأمان وتسجيل الدخول والتراخيص الحقيقية ---
if not st.session_state.logged_in:
    st.title("🛡️ ScaleBI Platform v3.0 - جدار الحماية والترخيص الصارم")
    tab_log, tab_reg = st.tabs(["🔒 تسجيل دخول المشتركين والأدمن", "🎟️ إنشاء حساب وتفعيل ترخيص تجاري جديد"])
    
    with tab_log:
        col_l1, col_l2, col_l3 = st.columns(3)
        with col_l2:
            in_email = st.text_input("البريد الإلكتروني للشركة:")
            in_pass = st.text_input("كلمة المرور الحالية:", type="password")
            
            if st.button("تحقق وولوج آمن للمنصة ⚡", use_container_width=True):
                conn = sqlite3.connect("scalebi_enterprise_v30.db")
                cursor = conn.cursor()
                cursor.execute("SELECT password_hash, store_name, sub_end, role FROM users WHERE email = ? AND is_active = 1", (in_email.strip(),))
                record = cursor.fetchone()
                conn.close()
                
                if record and record[0] == hash_pass(in_pass):
                    # 🛑 جدار التحقق الفعلي والصارم من تاريخ انتهاء الاشتراك!
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    expiration_date = record[2]
                    
                    if record[3] != 'admin' and expiration_date < today_str:
                        st.error(f"❌ انتهت صلاحية اشتراكك المدفوع بتاريخ ({expiration_date}). يرجى التواصل مع الإدارة للتجديد ودفع الـ 70 دينار.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.email = in_email.strip()
                        st.session_state.store_name = record[1]
                        st.session_state.sub_end_date = expiration_date
                        st.session_state.role = record[3]
                        st.success("تم التوثيق والتحقق من الاشتراك بنجاح!")
                        st.rerun()
                else:
                    st.error("بيانات الدخول خاطئة أو الحساب معطل.")
                    
    with tab_reg:
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r2:
            re_email = st.text_input("البريد الإلكتروني الجديد:")
            re_store = st.text_input("اسم متجرك الإلكتروني (سلة/زد):")
            re_pass = st.text_input("كلمة مرور الحساب:", type="password")
            re_key = st.text_input("كود الترخيص الصادر من الإدارة:")
            
            if st.button("تفعيل الحساب والتحقق من الترخيص 🚀", use_container_width=True):
                if not re_email or not re_key or not re_pass:
                    st.error("جميع الحقول إلزامية للتسجيل.")
                else:
                    conn = sqlite3.connect("scalebi_enterprise_v30.db")
                    cursor = conn.cursor()
                    
                    # 🛑 التحقق الصارم من وجود الترخيص وصلاحيته وعدم استخدامه مسبقاً!
                    cursor.execute("SELECT duration_days, is_used FROM master_licenses WHERE key = ?", (re_key.strip(),))
                    license_info = cursor.fetchone()
                    
                    if not license_info:
                        st.error("❌ كود الترخيص هذا غير موجود بالنظام أو غير صالح تماماً!")
                    elif license_info[1] == 1:
                        st.error("❌ كود الترخيص هذا تم استخدامه وتفعيله مسبقاً لحساب آخر!")
                    else:
                        # فحص تكرار البريد الإلكتروني
                        cursor.execute("SELECT email FROM users WHERE email = ?", (re_email.strip(),))
                        if cursor.fetchone():
                            st.error("هذا البريد مسجل مسبقاً في المنصة!")
                        else:
                            days_to_add = license_info[0]
                            start_dt = datetime.now().strftime('%Y-%m-%d')
                            end_dt = (datetime.now() + timedelta(days=days_to_add)).strftime('%Y-%m-%d')
                            
                            # إنشاء الحساب الجديد
                            cursor.execute("INSERT INTO users (email, password_hash, license_key, store_name, sub_start, sub_end, role) VALUES (?, ?, ?, ?, ?, ?, 'user')",
                                           (re_email.strip(), hash_pass(re_pass), re_key.strip(), re_store.strip(), start_dt, end_dt))
                            # وضع علامة "مستخدم" على كود الترخيص لمنع إعادة استعماله
                            cursor.execute("UPDATE master_licenses SET is_used = 1 WHERE key = ?", (re_key.strip(),))
                            conn.commit()
                            st.success(f"🎉 تفعيل حقيقي ناجح! اشتراكك متاح لمدة {days_to_add} يوماً حتى تاريخ ({end_dt}). توجه للدخول الآن.")
                    conn.close()

# --- بعد اجتياز جدار الحماية والدخول للمنصة ---
else:
    st.sidebar.title("💎 ScaleBI Platform v3.0")
    st.sidebar.write(f"👤 الحساب الحالي: {st.session_state.email}")
    st.sidebar.write(f"🏪 المنشأة: {st.session_state.store_name}")
    st.sidebar.write(f"📅 نهاية الاشتراك: {st.session_state.sub_end_date}")
    st.sidebar.write(f"🎖️ رتبة الحساب: {st.session_state.role.upper()}")
    
    if st.sidebar.button("🔒 تسجيل خروج آمن"):
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.session_state.role = "user"
        st.session_state.file_data = None
        st.rerun()
        
    st.markdown("---")

    # --- 4. لوحة الإدارة العليا وتوليد التراخيص الحقيقية (Admin Control Room) ---
    if st.session_state.role == "admin":
        st.header("👑 غُرفة عمليات الإدارة العليا والمطور (Admin Core)")
        st.write("بصفتك المطور الرئيسي، يمكنك من هنا توليد مفاتيح حقيقية بمدد زمنية محددة والتحكم المطلق بقواعد البيانات.")
        
        adm_col1, adm_col2 = st.columns(2)
        with adm_col1:
            st.subheader("🎟️ توليد وتشفير كود ترخيص مدفوع جديد")
            duration_choice = st.selectbox("مدة صلاحية الكود بالمستودع:", [30, 90, 365], format_func=lambda x: f"{x} يوماً")
            custom_key = st.text_input("كود مخصص أو اتركه للتوليد التلقائي:", value=f"SCALE-{np.random.randint(111,999)}-{np.random.randint(11,99)}")
            
            if st.button("إصدار وزرع الترخيص الفوري في النظام 💳"):
                conn = sqlite3.connect("scalebi_enterprise_v30.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO master_licenses (key, duration_days, is_used, generated_at) VALUES (?, ?, 0, ?)",
                               (custom_key.strip(), duration_choice, datetime.now().strftime('%Y-%m-%d')))
                conn.commit()
                conn.close()
                st.success(f"✅ تم إصدار الكود الحقيقي بنجاح: `{custom_key}` وهو متاح لتفعيل اشتراك مدته {duration_choice} يوماً للعميل الجديد.")
                
        with adm_col2:
            st.subheader("📋 حالة المفاتيح والمشتركين الحالية بالنظام")
            conn = sqlite3.connect("scalebi_enterprise_v30.db")
            lic_df = pd.read_sql_query("SELECT key as 'كود الترخيص', duration_days as 'المدة (أيام)', is_used as 'هل استُخدم؟' FROM master_licenses", conn)
            conn.close()
            st.dataframe(lic_df, use_container_width=True)
        st.markdown("---")

    # --- 5. واجهة معالجة وتقييم ذكاء الأعمال الفعلي للمتاجر ---
    st.header("📈 مركز الذكاء التحليلي والمحركات الاستراتيجية")
    
    if st.session_state.file_data is None:
        st.subheader("📥 خطوة 1: تغذية المنصة بالسجلات المحاسبية")
        uploaded_file = st.file_uploader("ارفع ملف المبيعات (سلة أو زد أو ملف معياري) Excel/CSV", type=["xlsx", "csv"])
        
        if st.button("🔄 محاكاة فحص متجر حقيقي واختبار محركات الـ 9.5/10 الشرسة", use_container_width=True):
            st.session_state.file_data = ScaleBIIntelligenceCore(None).generate_heavy_mock_data()
            st.rerun()
            
        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.file_data = pd.read_csv(uploaded_file)
            else:
                st.session_state.file_data = pd.read_excel(uploaded_file)
            st.rerun()
    else:
        # استدعاء وبناء محرك الأركان الأربعة المتقدمة
        core_engine = ScaleBIIntelligenceCore(st.session_state.file_data)
        cleaned_df, health_score, kpis, inventory_df, rfm_df = core_engine.process_all_engines()
        
        total_rev = cleaned_df['إجمالي_المبيعات'].sum()
        total_ord = cleaned_df['رقم_الطلب'].nunique() if 'رقم_الطلب' in cleaned_df.columns else len(cleaned_df)
        
        # حفظ اللقطة التلقائية السحابية المعزولة للعميل
        if st.button("💾 حفظ لقطة (Snapshot) سحابية من تقرير اليوم بذاكرة المنصة"):
            conn = sqlite3.connect("scalebi_enterprise_v30.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO report_history (email, report_date, revenue, orders_count, best_product) VALUES (?, ?, ?, ?, ?)",
                           (st.session_state.email, datetime.now().strftime('%Y-%m-%d %H:%M'), total_rev, total_ord, kpis.get('best_product', 'N/A')))
            conn.commit()
            conn.close()
            st.success("تم حفظ اللقطة بنجاح وعزلها برمجياً تحت إيميل منشأتك!")

        # الـ Executive Summary الذكي الصارم
        st.subheader("📋 1. الملخص التنفيذي وتفنيد الأداء القيادي")
        st.metric(label="مؤشر صحة ونظافة السجلات المحاسبية (Data Health Score)", value=f"{health_score}%")
        
        st.markdown(f"""
        > 🎯 **لوحة التوجيه والذكاء الحاد (KPI Enterprise Panel):**
        > * **صافي السيولة النقدية المستخلصة (الكاش الحقيقي):** {total_rev:,.2f} د.أ (مستبعد منها تماماً الطلبات الملغية والفاشلة لحمايتك من الأرقام الوهمية).
        > * **المنتج الحصان الرابح (الأعلى دخلاً):** **[{kpis.get('best_product', 'N/A')}]**.
        > * **العاصمة الشرائية الأكثر ولاءً لمتجرك:** **[{kpis.get('best_city', 'N/A')}]**.
        """)
        
        # تقسيم المنصة إلى ألسنة متطورة لعرض المحركات الأربعة المستحدثة
        tab_forecast, tab_inventory, tab_rfm, tab_history = st.tabs([
            "🔮 محرك التنبؤ الإحصائي (Linear Regression)", 
            "🚨 محرك مخاطر المخازن (Inventory Engine)", 
            "💎 تصنيف وتطهير العملاء (RFM Segmentation)",
            "📜 الأرشيف السحابي المعزول للشركة"
        ])
        
        with tab_forecast:
            st.subheader("🔮 التنبؤ الإحصائي بالمبيعات القادمة (مرحلة 1)")
            st.write("باستخدام خوارزمية الانحدار الخطي الرياضية السلسة، إليك حجم السيولة المتوقع دخولها للمتجر خلال الـ 7 أيام القادمة:")
            forecast_result = core_engine.run_predictive_forecasting()
            if not forecast_result.empty:
                f_col1, f_col2 = st.columns([1, 2])
                with f_col1:
                    st.dataframe(forecast_result, use_container_width=True)
                with f_col2:
                    # رسم بياني لخط الاتجاه المستقبلي المتوقع
                    st.line_chart(forecast_result.set_index('التاريخ المستقبلي'))
            else:
                st.info("البيانات الحالية قصيرة جداً زمنياً لبناء خط انحدار إحصائي موثوق.")
                
        with tab_inventory:
            st.subheader("🚨 محرك رصد مخاطر المخزون ومعدلات السحب اليومي (مرحلة 4)")
            st.write("تحليل حاد يحسب سرعة بيع كل قطعة ويحذرك كم يوماً متبقياً في مستودعك قبل النفاد والتوقف التام لتتخذ إجراءً فورياً مع الموردين:")
            st.dataframe(inventory_df.sort_values(by='الأيام_المتبقية_قبل_النفاد'), use_container_width=True)
            
        with tab_rfm:
            st.subheader("💎 محرك تصنيف وفصل العملاء الاستراتيجي (RFM Analysis - مرحلة 5)")
            st.write("لا تعامل عملائك بالتساوي! قمنا بفصل وتصنيف العملاء بناءً على سلوك الشراء الفعلي لتوجه عروضك التسويقية بذكاء:")
            
            rfm_counts = rfm_df['تصنيف_العميل'].value_counts()
            col_rfm1, col_rfm2 = st.columns([1, 2])
            with col_rfm1:
                st.write("📊 توزيع أعداد العملاء حسب الفئات:")
                st.dataframe(rfm_counts)
            with col_rfm2:
                st.write("🔍 قائمة تفصيلية بالعملاء وتصنيفاتهم الاستراتيجية لرصد المهددين بالمغادرة:")
                st.dataframe(rfm_df, use_container_width=True)
                
        with tab_history:
            st.subheader("📜 الأرشيف السحابي المعزول والخاص بمنشأتك")
            conn = sqlite3.connect("scalebi_enterprise_v30.db")
            history_df = pd.read_sql_query("SELECT report_date as 'تاريخ الفحص', revenue as 'السيولة الصافية', orders_count as 'عدد الطلبات', best_product as 'المنتج الأفضل' FROM report_history WHERE email = ?", conn, params=(st.session_state.email,))
            conn.close()
            
            if history_df.empty:
                st.info("لا توجد تقارير مؤرشفة سابقة لهذه المنشأة حالياً.")
            else:
                st.dataframe(history_df, use_container_width=True)

        if st.sidebar.button("🔄 تفريغ وفحص ملف جديد"):
            st.session_state.file_data = None
            st.rerun()

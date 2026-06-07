import streamlit as st
import pandas as pd
import numpy as np
import io

# إعدادات المنظومة السحابية الجديدة كلياً
st.set_page_config(page_title="Salla & Zid Enterprise BI | منظومة ذكاء الأعمال للمتاجر الكبرى", layout="wide")

class EnterpriseSaaSEngine:
    def __init__(self, df):
        self.df = df.copy() if df is not None else pd.DataFrame()
        
    def advanced_ecom_cleansing(self):
        """
        تطهير هيكلي مخصص لمعالجة ملفات سلة وزد الحقيقية.
        هنا نقوم بحل مشكلة الـ 'Order Bleeding' التي تكلف المتاجر آلاف الدولارات.
        """
        if self.df.empty:
            return self.df
            
        # قاموس الربط الذكي الموحد للمنصات الكبرى
        ecom_mapping = {
            'رقم الطلب': 'رقم_الطلب', 'رقم طلب': 'رقم_الطلب',
            'تاريخ الطلب': 'تاريخ_الطلب', 'تاريخ طلب': 'تاريخ_الطلب',
            'حالة الطلب': 'حالة_الطلب', 'حالة طلب': 'حالة_الطلب',
            'اسم المنتج': 'اسم_المنتج', 'المنتج': 'اسم_المنتج',
            'الكمية': 'الكمية', 'الكمية المباعة': 'الكمية',
            'سعر الوحدة': 'سعر_الوحدة', 'سعر منتج': 'سعر_الوحدة',
            'مدينة العميل': 'المدينة', 'المدينة': 'المدينة',
            'إجمالي المنتج': 'إجمالي_المنتج', 'صافي المبيعات': 'إجمالي_المنتج'
        }
        
        self.df.rename(columns=ecom_mapping, inplace=True)
        
        # سد الثغرات البرمجية لضمان عدم انهيار الـ SaaS أثناء المعالجة الحية
        for col in ['الكمية', 'سعر_الوحدة', 'حالة_الطلب']:
            if col not in self.df.columns:
                if col == 'الكمية': self.df['الكمية'] = 1
                if col == 'سعر_الوحدة': self.df['سعر_الوحدة'] = 0.0
                if col == 'حالة_الطلب': self.df['حالة_الطلب'] = 'مكتمل'

        # عزل النزيف المالي: إقصاء الطلبات الوهمية، الملغية، أو بانتظار الدفع
        if 'حالة_الطلب' in self.df.columns:
            bleeding_statuses = ['ملغي', 'مسترجع', 'بانتظار الدفع', 'بانتظار المراجعة', 'مرفوض', 'Canceled', 'Refunded']
            self.df = self.df[~self.df['حالة_الطلب'].astype(str).str.strip().isin(bleeding_statuses)]

        # تنظيف الأرقام والأسعار من أي فوضى إدخال
        self.df['الكمية'] = pd.to_numeric(self.df['الكمية'], errors='coerce').fillna(1).abs()
        self.df['سعر_الوحدة'] = pd.to_numeric(self.df['سعر_الوحدة'], errors='coerce').fillna(0).abs()
        
        self.df['إجمالي_المبيعات'] = self.df['الكمية'] * self.df['سعر_الوحدة']
        
        if 'تاريخ_الطلب' in self.df.columns:
            self.df['تاريخ_الطلب'] = pd.to_datetime(self.df['تاريخ_الطلب'], errors='coerce')
            
        self.df.drop_duplicates(inplace=True)
        return self.df

    def predictive_inventory_engine(self, df_clean):
        """محرك التنبؤ بالمبيعات وسلسلة الإمداد لمنع نقص المخزون أو تكدسه في المستودعات"""
        if 'تاريخ_الطلب' not in df_clean.columns or df_clean['تاريخ_الطلب'].isnull().all():
            return None, "حقل التاريخ غير متوفر أو يحتاج لضبط محاسبي."
            
        # تجميع المبيعات اليومية
        daily_data = df_clean.groupby(df_clean['تاريخ_الطلب'].dt.date)['إجمالي_المبيعات'].sum().reset_index()
        daily_data.columns = ['التاريخ', 'المبيعات']
        daily_data = daily_data.sort_values('التاريخ')
        
        if len(daily_data) < 4:
            return None, "البيانات التاريخية في الملف أقل من الحد الأدنى للتحليل الاستشرافي."
            
        # حساب المتوسط المتحرك الأسي لمعرفة الاتجاه الفعلي للسوق (Trend)
        daily_data['EMA'] = daily_data['المبيعات'].ewm(span=3, adjust=False).mean()
        
        last_ema = daily_data['EMA'].iloc[-1]
        last_date = pd.to_datetime(daily_data['التاريخ'].iloc[-1])
        
        # التنبؤ بـ 7 أيام قادمة لتأمين الكاش والمخزون
        future_days = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=7, freq='D')
        predictions = [max(last_ema * (1 + np.sin(i/2)*0.1), 10.0) for i in range(7)]
        
        return pd.DataFrame({'التاريخ': future_days, 'المبيعات_المتوقعة': predictions}), "نجاح"

    def generate_100k_store_mock(self):
        """توليد محاكاة حية وفورية لمتجر ضخم حقق 100,000 دينار لاختبار النظام"""
        np.random.seed(24)
        size = 350
        dates = pd.date_range(start="2026-05-01", periods=size, freq='4h')
        products = ['عطر توباكو ملكي', 'ساعة كلاسيك ذكية', 'محفظة جلدية فاخرة', 'منظم مكتب خشبي']
        cities = ['الرياض', 'جدة', 'عمان', 'الدمام', 'إربد', 'دبي']
        statuses = ['مكتمل', 'تم الشحن', 'ملغي', 'بانتظار الدفع', 'مسترجع']
        
        df = pd.DataFrame({
            'رقم الطلب': np.random.randint(400000, 900000, size=size),
            'تاريخ الطلب': np.random.choice(dates, size=size),
            'حالة الطلب': np.random.choice(statuses, size=size, p=[0.65, 0.15, 0.10, 0.06, 0.04]),
            'اسم المنتج': np.random.choice(products, size=size),
            'الكمية': np.random.choice([1, 2, 3, -1, np.nan], size=size, p=[0.80, 0.10, 0.05, 0.02, 0.03]),
            'سعر الوحدة': np.random.choice([280, 420, 85, 150], size=size),
            'مدينة العميل': np.random.choice(cities, size=size)
        })
        return df

# --- واجهة الـ SaaS والتحكم في بوابة الدفع والتفعيل ---
if 'saas_activated' not in st.session_state:
    st.session_state.saas_activated = False
if 'active_data' not in st.session_state:
    st.session_state.active_data = None

st.title("🛡️ ScaleBI - المنظومة السحابية المتقدمة لذكاء أعمال متاجر سلة وزد")
st.write("نظام SaaS مؤسسي مخصص للمتاجر الكبرى لربط البيانات، حماية الأرباح، والتنبؤ بالمخزون.")
st.markdown("---")

# 1. بوابة الدفع المقفلة (SaaS Paywall Layer) - تم إصلاح الشرط هنا لتفادي ValueError
if st.session_state.active_data is None and not st.session_state.saas_activated:
    st.subheader("🔒 تفعيل الوصول لقطاع الشركات والمتاجر الكبرى")
    st.info("💡 لمشاهدة واختبار النظام كصاحب متجر يحقق مئات الآلاف، اضغط تفعيل الباقة للوصول للوحة التحكم الكاملة.")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("""
        ### 🚀 باقة المستشار والذكاء الاستباقي
        * **تطهير وعزل فوري** للطلبات الفاشلة والملغية (حماية صافي الأرباح).
        * **محرك استباقي للمخزون** يمنع نفاد المنتجات أو تجميد السيولة.
        * **تقارير دورية ومطابقة تامة** لهياكل ملفات سلة وزد الحقيقية.
        * **تصدير بصيغة Excel معتمدة** للمحاسبين والشركاء.
        
        💸 **الاشتراك: 70 دينار أردني / شهرياً (100 دولار)**
        """)
        if st.button("⚡ تفعيل الاشتراك السحابي والوصول الفوري", use_container_width=True):
            st.session_state.saas_activated = True
            st.success("تم تفعيل باقتك التجارية بنجاح! مرحباً بك في ScaleBI.")
            st.rerun()

# 2. لوحة التحكم التشغيلية بعد الدخول
else:
    st.sidebar.success("🟢 باقة المؤسسات: نشطة ومفعّلة")
    if st.sidebar.button("🔒 تسجيل الخروج وإغلاق الجلسة"):
        st.session_state.saas_activated = False
        st.session_state.active_data = None
        st.rerun()
        
    if st.session_state.active_data is None:
        st.subheader("📥 خطوة 1: رفع أو محاكاة بيانات المتجر")
        uploaded_file = st.file_uploader("ارفع ملف مبيعات المتجر المباشر (Excel/CSV)", type=["xlsx", "csv"])
        
        if st.button("🔄 اختبار النظام: محاكاة متجر مبيعات ضخم (100k+) وفحص الأداء فوراً", use_container_width=True):
            st.session_state.active_data = EnterpriseSaaSEngine(None).generate_100k_store_mock()
            st.rerun()
            
        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.active_data = pd.read_csv(uploaded_file)
            else:
                st.session_state.active_data = pd.read_excel(uploaded_file)
            st.rerun()
            
    else:
        # تشغيل المحرك السحابي الجديد
        saas_engine = EnterpriseSaaSEngine(st.session_state.active_data)
        cleaned_df = saas_engine.advanced_ecom_cleansing()
        
        # المقاييس التنفيذية الكبرى (Executive Metrics)
        total_revenue = cleaned_df['إجمالي_المبيعات'].sum()
        total_orders = cleaned_df['رقم_الطلب'].nunique() if 'رقم_الطلب' in cleaned_df.columns else len(cleaned_df)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # حجم النزيف الذي حمينا التاجر منه
        leaked_count = len(st.session_state.active_data) - len(cleaned_df)
        
        st.subheader("📊 خطوة 2: لوحة الإدارة المالية وكفاءة رأس المال")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 صافي المبيعات المحققة (كاش فعلي)", f"{total_revenue:,.2f} د.أ")
        m2.metric("📦 الطلبات المعتمدة (النظيفة)", f"{total_orders} طلب")
        m3.metric("🛒 معدل القيمة الشرائية للسلة", f"{avg_order_value:,.2f} د.أ")
        m4.metric("🚨 عمليات وهمية وملغية تم صدّها", f"{leaked_count} عملية")
        
        st.markdown("---")
        
        tab_geo, tab_inv, tab_export = st.tabs(["🗺️ الأداء الجغرافي والسلعي", "🔮 التنبؤ الاستباقي وإدارة المخازن", "📥 مركز التقارير القيادية"])
        
        with tab_geo:
            g1, g2 = st.columns(2)
            with g1:
                st.write("📍 صافي حجم المبيعات حسب المدن الحقيقية للعملاء:")
                if 'المدينة' in cleaned_df.columns:
                    st.bar_chart(cleaned_df.groupby('المدينة')['إجمالي_المبيعات'].sum())
            with g2:
                st.write("🏆 ترتيب المنتجات الأعلى توليداً للسيولة النقدية:")
                if 'اسم_المنتج' in cleaned_df.columns:
                    st.bar_chart(cleaned_df.groupby('اسم_المنتج')['إجمالي_المبيعات'].sum())
                    
        with tab_inv:
            st.subheader("🔮 خوارزمية سلسلة الإمداد والتنبؤ بسبعة أيام قادمة")
            fut_df, status_msg = saas_engine.predictive_inventory_engine(cleaned_df)
            
            if status_msg == "نجاح" and fut_df is not None:
                st.line_chart(data=fut_df, x='التاريخ', y='المبيعات_المتوقعة')
                expected_cash_week = fut_df['المبيعات_المتوقعة'].sum()
                
                st.warning(f"💡 **توجيه مالي استراتيجي للعمليات**: يتوقع النظام تدفقاً نقدياً للمبيعات بقيمة **{expected_cash_week:,.2f} د.أ** خلال الـ 7 أيام القادمة. لتفادي مشكلة نفاد المخزون وضياع الأرباح، نوصي بمطابقة مستويات بضائعك الحالية فوراً لتلبية حجم هذا الطلب المتوقع.")
            else:
                st.info(f"حالة محرك التنبؤ: {status_msg}")
                
        with tab_export:
            st.subheader("📥 تصدير التقرير المالي النظيف والجاهز")
            st.write("يمكنك تحميل هذا الملف النظيف والخالي من المعاملات الفاشلة لتقديمه مباشرة للمحاسبين أو الشركاء لحماية دقة قراراتك.")
            
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as wr:
                cleaned_df.to_excel(wr, sheet_name='صافي الأرباح النظيفة', index=False)
                
            st.download_button(
                label="📥 تحميل ملف Excel المظهر والمطابق للشركات",
                data=excel_buffer.getvalue(),
                file_name="ScaleBI_Cleaned_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

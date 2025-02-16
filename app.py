import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime
from openpyxl.drawing.image import Image as OpenpyxlImage

def init_db():
    conn = sqlite3.connect('software_checks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS checks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  sp_name TEXT,
                  responsible TEXT,
                  po_name TEXT,
                  object TEXT,
                  works_count INTEGER,
                  responsibility_zone TEXT,
                  start_time TEXT,
                  end_time TEXT,
                  personnel_count INTEGER,
                  checks_count INTEGER,
                  violations_count INTEGER,
                  violation_type TEXT,
                  kpb_violation TEXT,
                  kpb_detected INTEGER,
                  act_issued INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS organizations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT)''')
    conn.commit()
    conn.close()

def add_organization(name):
    conn = sqlite3.connect('software_checks.db')
    c = conn.cursor()
    c.execute("INSERT INTO organizations (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_organizations():
    conn = sqlite3.connect('software_checks.db')
    c = conn.cursor()
    c.execute("SELECT name FROM organizations")
    organizations = c.fetchall()
    conn.close()
    return [org[0] for org in organizations]

def add_record(data):
    conn = sqlite3.connect('software_checks.db')
    c = conn.cursor()
    c.execute('''INSERT INTO checks 
                 (date, sp_name, responsible, po_name, object, works_count, responsibility_zone, 
                  start_time, end_time, personnel_count, checks_count, violations_count, 
                  violation_type, kpb_violation, kpb_detected, act_issued) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()

def get_records():
    conn = sqlite3.connect('software_checks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM checks")
    records = c.fetchall()
    conn.close()
    return records

def delete_record(record_id):
    conn = sqlite3.connect('software_checks.db')
    c = conn.cursor()
    c.execute("DELETE FROM checks WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

def update_record(data):
    conn = sqlite3.connect('software_checks.db')
    c = conn.cursor()
    c.execute("UPDATE checks SET date=?, sp_name=?, responsible=? WHERE id=?", data)
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="Проверки ПО в СП", layout="wide")
    init_db()
    
    st.title("Проверки ПО в СП - Веб версия")
    
    # Секция управления организациями
    with st.expander("Управление организациями (ПО)"):
        with st.form("org_form"):
            new_po = st.text_input("Добавить новое ПО")
            if st.form_submit_button("Добавить"):
                if new_po:
                    add_organization(new_po)
                    st.rerun()
        
        po_list = get_organizations()
        if po_list:
            st.write("Список доступных ПО:")
            st.write(po_list)
        else:
            st.warning("Нет зарегистрированных организаций")

    # Секция для добавления новой записи
    with st.expander("Добавить новую запись", expanded=True):
        with st.form("add_record_form"):
            cols = st.columns(2)
            date = cols[0].date_input("Дата*")
            sp_name = cols[1].selectbox("Наименование СП*", ["АТУ", "УЖДТ"])
            
            responsible = st.text_input("Ответственный от СП*")
            po_name = st.selectbox("Наименование ПО*", get_organizations())
            
            cols2 = st.columns(2)
            object = cols2[0].text_input("Объект/Участок")
            works_count = cols2[1].number_input("Кол-во выполняемых работ*", min_value=0)
            
            responsibility_zone = st.text_input("Зона ответственности (СП)")
            
            cols3 = st.columns(2)
            start_time = cols3[0].time_input("Время начала работ*")
            end_time = cols3[1].time_input("Время окончания работ*")
            
            cols4 = st.columns(2)
            personnel_count = cols4[0].number_input("Кол-во персонала ПО*", min_value=0)
            checks_count = cols4[1].number_input("Проведено проверок*", min_value=0)
            
            violations_count = st.number_input("Количество нарушений*", min_value=0)
            
            violation_type = st.selectbox("Тип нарушения*", [
                "Работы на высоте", "Огневые работы/Пожарная безопасность", 
                "Грузоподъёмные работы/Работа с ПС", "Электробезопасность", 
                "Работы в газоопасн. местах/замкнутом простр-ве", 
                "Земляные работы", "Документы/Допуски и удостоверения", 
                "Исправность инструментов и приспособлений", 
                "Применение/Исправность СИЗ", 
                "Содержание территории/рабочих мест", 
                "Безопасность дорожного движения"
            ])
            
            kpb_violation = st.selectbox("Нарушения КПБ*", [
                "Нет алкоголю и наркотикам", "Сообщай о происшествиях", 
                "Получи допуск", "Защити себя от падения"
            ])
            
            act_issued = st.selectbox("Оформлен Акт*", ["Да", "Нет"])
            
            if st.form_submit_button("Добавить запись"):
                data = (
                    date.strftime("%d.%m.%Y"),
                    sp_name,
                    responsible,
                    po_name,
                    object,
                    works_count,
                    responsibility_zone,
                    start_time.strftime("%H:%M"),
                    end_time.strftime("%H:%M"),
                    personnel_count,
                    checks_count,
                    violations_count,
                    violation_type,
                    kpb_violation,
                    1 if kpb_violation else 0,
                    1 if act_issued == "Да" else 0
                )
                add_record(data)
                st.success("Запись успешно добавлена!")
                st.rerun()

    # Секция просмотра и управления записями
    with st.expander("Просмотр и управление записями"):
        records = get_records()
        df = pd.DataFrame(records, columns=[
            "ID", "Дата", "СП", "Ответственный", "ПО", "Объект", "Работы", 
            "Зона", "Начало", "Конец", "Персонал", "Проверки", "Нарушения",
            "Тип нарушения", "КПБ", "Выявлено КПБ", "Акт"
        ])
        
        st.dataframe(df, use_container_width=True)
        
        with st.form("edit_form"):
            cols = st.columns(3)
            selected_id = cols[0].number_input("ID записи для редактирования", min_value=1)
            edit_date = cols[1].date_input("Новая дата")
            edit_sp_name = cols[2].selectbox("Новое наименование СП", ["АТУ", "УЖДТ"])
            
            edit_responsible = st.text_input("Новый ответственный")
            
            if st.form_submit_button("Сохранить изменения"):
                update_data = (
                    edit_date.strftime("%d.%m.%Y"),
                    edit_sp_name,
                    edit_responsible,
                    selected_id
                )
                update_record(update_data)
                st.success("Изменения сохранены!")
                st.rerun()

        with st.form("delete_form"):
            del_id = st.number_input("ID записи для удаления", min_value=1)
            if st.form_submit_button("Удалить запись"):
                delete_record(del_id)
                st.success("Запись удалена!")
                st.rerun()

    # Секция аналитики
    with st.expander("Аналитика и отчеты"):
        po_list = get_organizations()
        selected_po = st.selectbox("Выберите ПО", po_list)
        
        cols = st.columns(2)
        start_date = cols[0].date_input("Начальная дата")
        end_date = cols[1].date_input("Конечная дата")
        
        if st.button("Сгенерировать график"):
            conn = sqlite3.connect('software_checks.db')
            query = f"""
                SELECT date, violations_count 
                FROM checks 
                WHERE po_name = '{selected_po}' 
                AND date BETWEEN '{start_date.strftime("%d.%m.%Y")}' AND '{end_date.strftime("%d.%m.%Y")}'
            """
            df = pd.read_sql(query, conn)
            conn.close()
            
            fig, ax = plt.subplots()
            ax.plot(df['date'], df['violations_count'], marker='o')
            ax.set_xlabel("Дата")
            ax.set_ylabel("Количество нарушений")
            ax.set_title(f"Нарушения для {selected_po}")
            st.pyplot(fig)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Данные', index=False)
                
                buf = io.BytesIO()
                fig.savefig(buf, format='png')
                buf.seek(0)
                
                workbook = writer.book
                worksheet = workbook.create_sheet('График')
                img = OpenpyxlImage(buf)
                worksheet.add_image(img, 'A1')
            
            output.seek(0)
            st.download_button(
                label="Скачать отчет",
                data=output,
                file_name=f"отчет_{selected_po}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()

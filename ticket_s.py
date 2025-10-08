import streamlit as st
from db import execute_query,fetch_query
from security import hash_password ,verify_password
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from password_email import password
import smtplib
# Ticket System Application
# This application allows users to create, view, and update tickets.
st.set_page_config(page_title='Ticket System 🎫',layout='wide')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.Name = None
    st.session_state.role = None

if 'password_change_logs' not in st.session_state:
    st.session_state.password_change_logs=[]

def notify_password_change(old_password, new_password, employee_name):
     msg=f"✅ Password changed from '{old_password}' to '{new_password}' by employee: {employee_name}"
     return msg


def send_email(to_email,subject, message):
    query='''
    SELECT * FROM IT_Info WHERE Name=?'''
    sender_email = "taskmangment62@gmail.com"  
    sender_password = password()
    #to_email='yossifhendy32@gmail.com'
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"error  {e}")
        return False
    
def create_ticket(username,title,description,position):
    query='''
    INSERT INTO T_TK(UserName,Title, Description,Position)
    VALUES (?,?,?,?)
    '''
    execute_query(query,(username,title,description,position))

def get_tickets():
    query='''
    SELECT * FROM T_TK
    '''
    ticket=fetch_query(query)
    return ticket 

def view_my_Tickets(name):
    query='''
    SELECT * FROM T_TK WHERE UserName=?
    '''
    tickets=fetch_query(query, (name,))
    return tickets

def em_to(to_email):
    new='Pending'
    if to_email=='yossifhendy32@gmail.com':
         new='Youssef'
    elif to_email=='hassan.gamal.it@gmail.com':
        new='Hassan'
    elif to_email=='Adham.omar@almada-eg.com':
        new='Adham'
    return new

#hassan.gamal.it@gmail.com
#haasan.gamal@almada-eg.com    
def update_ticket_status(ticket_id, new_status):
    query = 'UPDATE T_TK SET Status = ? WHERE FormattedID = ?'
    execute_query(query, (new_status, ticket_id))
    
def update_tiket_touser(ticket_id, new_status):
    query=''' UPDATE T_TK SET Status =? WHERE FormattedID= ?'''
    execute_query(query,(new_status,ticket_id))   
     
def update_assignto(ticket_id,new):
    query='''UPDATE T_TK SET assignto =? WHERE FormattedID= ? '''
    execute_query(query,(new,ticket_id))
    
def logout():
    st.session_state.logged_in= False
    st.session_state.Name = None
    st.session_state.Role= None
    st.success('Logged out successfully ✅')
    
def Login():
    st.subheader('Login Page 🔐')
    id_input= st.text_input('ID')
    password_input = st.text_input('Password', type='password')
    
    if st.button('Login'):
         query='''
              SELECT * FROM IT_Info WHERE ID=?
         '''
    
         result=fetch_query(query, (id_input,))
         if not result:
            st.write('User not found ❌')
            return
    
         user_data=result[0]
         hashed_password=str(user_data[3]).strip()
         role=user_data[4]
         if verify_password(password_input,hashed_password):
            st.session_state.logged_in =True
            st.session_state.ID= id_input
            st.session_state.Role=role
            st.success(f"Login Successful as {id_input} ✅")
         else:
            st.error("❌ Incorrect password")
            
def change_pass(old,new):
    
    query='''
    SELECT * FROM IT_Info WHERE ID=?'''
    
    id=st.session_state.ID
    result=fetch_query(query,(id,))
    
    if not result:
        st.write('User not found')
    user_data=result[0]
    name=user_data.Name
    hashed_password=user_data.password
    if verify_password(old,hashed_password):
            new_hashed_password= hash_password(new)
            update_query='''
            UPDATE IT_Info SET password=? WHERE Name=?
            '''
            execute_query(update_query, (new_hashed_password, name)) 
            st.success('Password changed successfully ✅')   
    else:
        st.error('incorrect password ')    
            
             


              
def main_application():
    st.title('Task Mangement')
    query='''SELECT * FROM IT_Info WHERE ID=?'''
    id = st.session_state.ID
    result=fetch_query(query, (id,))
    if not result:
        st.write('User not found ❌')
        
    user_data=result[0]
    name=user_data[1]
    hashed_password=str(user_data[3]).strip()
    role=user_data[4]
    position=user_data[2]
    st.sidebar.write(f'Welcome {name} 👋')

    if role=='assigner':
        menu=st.sidebar.selectbox('Menu',['View Tickets','Update Ticket Status','update password','task assignment','Create Ticket'])
        if menu=='Update Ticket Status':
                st.subheader('Update Ticket Status')
                ticket_id = st.text_input('FormattedID')
                new_status= st.selectbox('New Status',['Received','In Progress','fixed','Closed'])
                if st.button('Update Status'):
                    if ticket_id and new_status:
                        update_ticket_status(ticket_id, new_status)
                        sub=f'update status'
                        mess=f'i am {name}\n\n, ticket with ID {ticket_id} has been updated to {new_status}'
                        send_email('ahmed.abdellatif@almada-eg.com',sub,mess)
                        st.success(f'Ticket {ticket_id} status updated to {new_status} ✅')
                    else:
                        st.error('Please provide Ticket ID and New Status ❌')
        
        elif menu=='Create Ticket':
                 st.subheader('Create Ticket ')
                 title=st.selectbox('Ticket Title',['IT Ticket'])
                 description=st.text_area('Ticket Description')
                 final_description = f'Hi i am {name},id equal:{id},\n\n {description}'
                 send_email('ahmed.abdellatif@almada-eg.com',title,final_description)
                 if st.button('Create Ticket'):
                    if title and description:
                      create_ticket(name, title,final_description,position)
                      st.success('Ticket created successfully ✅')
                    else:
                       st.error('Please provide Title and Description ❌')
                     
                       
        elif menu=='View Tickets':
                st.subheader('View Tickets')
                if st.button('Refresh Ticket'):
                    tickets=get_tickets()
                    if tickets:
                      data=[]
                      for i in tickets:
                        data.append({
                            'Ticket ID': i.TicketID,
                            'assign_to':i.assignto,
                            'Title': i.Title,
                            'Description': i.Description,
                            'Status': i.Status,
                            'UserName': i.UserName,
                            'FormattedID':i.FormattedID,
                            'position': i.Position
                        })
                      st.dataframe(pd.DataFrame(data),use_container_width=True)    
                                             
                    else:
                        st.write('No tickets found ❌')
        
        elif menu=='update password':
                st.subheader('Change Password')
                old=st.text_input('Old Password',type='password')
                new=st.text_input('New Password',type='password')
                if st.button('Change Password'):
                    if old and new:
                        change_pass(old,new)
                        msg=notify_password_change(old,new,name)
                        send_email('yossifhendy32@gmail.com','change_password',msg)
                    else:
                        st.error('Please inter Old password and new password')     
                                                                                    
        elif menu=='task assignment':
            st.subheader('Task Assignment ')
            st.write(f'Hi {name} you need to assign the tasks based on the issue. Here are three person :-->[Hassan , Adham] ')
            #def send_email(to_email,subject, message):
            to_email=st.selectbox('send_to',['hassan.gamal.it@gmail.com','Adham.omar@almada-eg.com'])
            description=st.text_area('Paste the description')
            idd=st.text_input('Paste FormattedID')
            mess=f'description:{description} and ID Ticket:{idd}'          
            if st.button('Send'):
                if to_email and description and idd:
                    send_email(to_email,'Task',mess)
                    news=em_to(to_email)
                    update_assignto(idd,news)
                        
                    st.success('Task sent successfully ✅')
                else:
                    st.error('please inter the description and id ')
        
    elif role=='Topadmin':
        menu=st.sidebar.selectbox('Menu',['View Tickets','Update Ticket Status','update password','Create Ticket'])
        if menu=='Update Ticket Status':
           st.subheader('Update Ticket Status')
           ticket_id = st.text_input('FormattedID')
           new_status= st.selectbox('New Status',['Received','In Progress','fixed','Closed'])
           if st.button('Update Status'):
               if ticket_id and new_status:
                   update_ticket_status(ticket_id, new_status)
                   sub=f'update status'
                   mess=f'i am {name}\n\n, ticket with ID {ticket_id} has been updated to {new_status}'
                   send_email('ahmed.abdellatif@almada-eg.com',sub,mess)
                   st.success(f'Ticket {ticket_id} status updated to {new_status} ✅')
               else:
                        st.error('Please provide Ticket ID and New Status ❌')
                        
        elif menu=='update password':
                st.subheader('Change Password')
                old=st.text_input('Old Password',type='password')
                new=st.text_input('New Password',type='password')
                if st.button('Change Password'):
                    if old and new:
                        change_pass(old,new)
                        msg=notify_password_change(old,new,name)
                        send_email('yossifhendy32@gmail.com','change_password',msg)
                        
                    else:
                        st.error('Please inter Old password and new password') 
                        
                                           
       
        
        elif menu=='View Tickets':
                st.subheader('View Tickets')
                if st.button('Refresh Ticket'):
                    tickets=get_tickets()
                    if tickets:
                      data=[]
                      for i in tickets:
                        data.append({
                            'Ticket ID': i.TicketID,
                            'assign_to':i.assignto,
                            'Title': i.Title,
                            'Description': i.Description,
                            'Status': i.Status,
                            'UserName': i.UserName,
                            'FormattedID':i.FormattedID,
                            'position': i.Position
                        })
                      st.dataframe(pd.DataFrame(data),use_container_width=True)    
                                             
                    else:
                        st.write('No tickets found ❌')
            
        elif menu=='Create Ticket':
                 st.subheader('Create Ticket ')
                 title=st.selectbox('Ticket Title',['IT Ticket'])
                 description=st.text_area('Ticket Description')
                 final_description = f'Hi i am {name},id equal:{id},\n\n {description}'
                 send_email('ahmed.abdellatif@almada-eg.com',title,final_description)
                 if st.button('Create Ticket'):
                    if title and description:
                      create_ticket(name, title,final_description,position)
                      st.success('Ticket created successfully ✅')
                    else:
                       st.error('Please provide Title and Description ❌')
                        
    elif  role == 'admin':
            menu= st.sidebar.selectbox('Menu',['View Tickets','Update Ticket Status','update password','Create Ticket'])
             
            if menu=='Update Ticket Status':
                st.subheader('Update Ticket Status')
                ticket_id = st.text_input('FormattedID')
                new_status= st.selectbox('New Status',['Received','In Progress','fixed','Closed'])
                if st.button('Update Status'):
                    if ticket_id and new_status:
                        update_ticket_status(ticket_id, new_status)
                        sub=f'update status'
                        mess=f'i am {name}\n\n, ticket with ID {ticket_id} has been updated to {new_status}'
                        send_email('ahmed.abdellatif@almada-eg.com',sub,mess)
                        st.success(f'Ticket {ticket_id} status updated to {new_status} ✅')
                    else:
                        st.error('Please provide Ticket ID and New Status ❌')
                        
            elif menu=='Create Ticket':
                 st.subheader('Create Ticket ')
                 title=st.selectbox('Ticket Title',['IT Ticket'])
                 description=st.text_area('Ticket Description')
                 final_description = f'Hi i am {name},id equal:{id},\n\n {description}'
                 send_email('ahmed.abdellatif@almada-eg.com',title,final_description)
                 if st.button('Create Ticket'):
                    if title and description:
                      create_ticket(name, title,final_description,position)
                      st.success('Ticket created successfully ✅')
                    else:
                      st.error('Please provide Title and Description ❌')

            elif menu=='View Tickets':
                st.subheader('View Tickets')
                if st.button('Refresh Ticket'):
                    tickets=get_tickets()
                    if tickets:
                      data=[]
                      for i in tickets:
                        data.append({
                            'Ticket ID': i.TicketID,
                            'assign_to': i.assignto,
                            'Title': i.Title,
                            'Description': i.Description,
                            'Status': i.Status,
                            'UserName': i.UserName,
                            'FormattedID':i.FormattedID,
                            'position':i.Position
                        })
                      st.dataframe(pd.DataFrame(data),use_container_width=True)    
                                             
                    else:
                        st.write('No tickets found ❌')
            
            elif menu=='update password':
                st.subheader('Change Password')
                old=st.text_input('Old Password',type='password')
                new=st.text_input('New Password',type='password')
                if st.button('Change Password'):
                    if old and new:
                        change_pass(old,new)
                        msg=notify_password_change(old,new,name)
                        send_email('yossifhendy32@gmail.com','change_password',msg)
                    else:
                        st.error('Please inter Old password and new password')
                              
    # if the user is a regular user
    
    elif role =='User':
        menu= st.sidebar.selectbox('Menu',['Create ticket','View Tickets','update password'])
        if menu=='Create ticket':
            st.subheader('Create Ticket')
            title=st.selectbox('Ticket Title',['IT Ticket'])
            description=st.text_area('Ticket Description')
            final_description = f'Hi i am {name},id equal:{id},\n\n {description}'
            send_email('ahmed.abdellatif@almada-eg.com',title,final_description)
            send_email('hassan.gamal.it@gmail.com',title,final_description)
            send_email('yossifhendy32@gmail.com',title,final_description)
            if st.button('Create Ticket'):
                if title and description:
                    create_ticket(name, title,final_description,position)
                    st.success('Ticket created successfully ✅')
                else:
                    st.error('Please provide Title and Description ❌')
        elif menu=='View Tickets':
            st.subheader('View Tickets')
            if st.button('Refresh Ticket'):
                tickets=view_my_Tickets(name)
                data=[]
                if tickets:
                    for i in tickets:
                        st.write("-"*20)
                        st.write(f'Ticket ID: **{i.TicketID}**  / Title: **{i.Title}** / description:**{i.Description}** / status: ***{i.Status}*** / username: **{i.UserName}** / FormattedID: **{i.FormattedID}** / posstion: **{i.Position}**')
                        
                else:
                    st.write('No tickets found ❌') 
           
        elif menu=='update password':
            st.header('Change password')
            old=st.text_input('Old Password', type='password')
            new=st.text_input('New Password', type='password')
            if st.button('update password'):
              if old and new:   
                 change_pass(old,new)
                 msg=notify_password_change(old,new,name)
                 send_email('yossifhendy32@gmail.com','change_password',msg)
              else:
                  st.error('Please provide new password and old password ❌')
                    
                    
# Add a logout button
st.sidebar.button('Logout', on_click=logout)

if __name__== '__main__':
    st.sidebar.title('Ticket System Menu')
    if not st.session_state.logged_in:
        Login()
    else:
        main_application()



 #py -m streamlit run ticket_sys.py
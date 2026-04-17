import streamlit as st
import os
import json
import datetime
from openai import OpenAI

# 页面配置
st.set_page_config(
    page_title="AI智能助理",
    page_icon="🤖",
    #布局
    layout="wide",
    #控制侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={}
)

#定义保存会话信息的函数
def save_session():
    if st.session_state.current_session:
            #构建新的会话对象
            session_date={
                "nick_name":st.session_state.nick_name,
                "character":st.session_state.character,
                "current_session":st.session_state.current_session,
                "messages":st.session_state.messages
            }
            #如果sessions目录不存在，则创建
            if not os.path.exists("sessions"):
                os.makedirs(os.path.join("practical_case_studies/ai_partner", "sessions"),exist_ok=True)
            #2.保存会话信息
            with open(f"practical_case_studies/ai_partner/sessions/{st.session_state.current_session}.json","w",encoding="utf-8") as f:
                json.dump(session_date,f,ensure_ascii=False,indent=4)

#生成会话标识函数
def generate_session_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

#加载所有对话信息函数
def load_sessions():
    session_list = []
    #加载目录下的所有会话文件
    if os.path.exists("practical_case_studies/ai_partner/sessions"):
        file_list=os.listdir("practical_case_studies/ai_partner/sessions")
        for file_name in file_list:
            if file_name.endswith(".json"):
                session_list.append(file_name[:-5])
    session_list.sort(reverse=True)#排序，降序排序
    return session_list

#加载指定对话信息函数
def load_session(session_name):
    try:
        if os.path.exists(f"practical_case_studies/ai_partner/sessions/{session_name}.json"):
            with open(f"practical_case_studies/ai_partner/sessions/{session_name}.json","r",encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.character = session_data["character"]
                st.session_state.current_session = session_name
    except Exception as e:
        st.error("加载会话信息失败！")

#删除指定会话信息函数
def delete_session(session_name):
    try:
        if os.path.exists(f"practical_case_studies/ai_partner/sessions/{session_name}.json"):
            os.remove(f"practical_case_studies/ai_partner/sessions/{session_name}.json")
            #若删除的是当前会话，则更新消息列表
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除会话信息失败！")

#创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY 环境变量的名字，值就是DeepSeek的API_KEY的))

# 手动输入模型地址和密钥
user_web = input("请输入您所用大模型的Web：")
api_key = input("请输入DeepSeek的API_KEY：")
# 初始化客户端
client = OpenAI(
    api_key=api_key,       # 直接用你输入的变量，不加引号
    base_url=user_web      # 直接用你输入的变量，不加引号
)
print("客户端初始化成功！")

#大标题
st.title("AI智能助理")

#系统提示词
system_prompt = """
        你叫%s，现在是用户的助理，请完全代入助理角色。：
        规则：
            1. 每次只回1条消息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像微信聊天一样，或者回复像助理汇报一样
            5.用符合助理性格的方式对话
            6. 回复的内容, 要充分体现助理的性格特征
        助理性格：
            - %s
        你必须严格遵守上述规则来回复用户。
    """


#初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "Ryder1号"
# 性格
if "nature" not in st.session_state:
    st.session_state.nature = "理性客观的职场男人"
#会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()#符号分别表示年、月、日、时、分、秒

#展示聊天记录
st.text(f"会话名称:{st.session_state.current_session}")
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])




#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "Ryder1号"
#性格
if "character" not in st.session_state:
    st.session_state.character = "理性客观的职场男人"

# 创建左侧侧边栏
with st.sidebar:
    st.subheader("AI控制面板")
    #新建会话
    if st.button("新建会话",width="stretch",icon="➕️"):
        #1.保存当前会话信息
        save_session()
        #2.创建新会话
        if st.session_state.messages:#聊天记录非空情况创建新会话，否则返回false则不创建新会话
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            # st.rerun()#重新运行当前页面

    #会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1,col2=st.columns([8,2])
        with col1:
            #加载会话信息
            if st.button(session,icon="📑",key=f"load_{session}",type="primary" if session==st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            #删除会话信息
            if st.button("",icon="❌️",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    #分割线
    st.divider()
    
    st.subheader("助理信息")
    nick_name=st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    character=st.text_area("性格",placeholder="请输入伴侣性格",value=st.session_state.character)
    if character:
        st.session_state.character = character



#消息输入框
prompt = st.chat_input("请输入你的问题")
if prompt:#字符串会自动转换为布尔值，如果字符串非空，则为True;""否则为False
    st.chat_message("user").write(prompt)
    print("--------->调用AI大模型，提示词：",prompt)
    #保存用户输入的提示词
    st.session_state.messages.append({"role":"user","content":prompt})
    #调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name,st.session_state.character)},
            *st.session_state.messages
        ],
        stream=True
    )

    #输出大模型的返回结果(非流式输出)
    # print("<-----------大模型返回的结果：",response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)
    #输出大模型的返回结果(流式输出)
    response_message = st.empty()#创建一个空的组件，用于显示大模型返回的结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content=chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)


    #保存ai大模型的返回结果
    st.session_state.messages.append({"role":"assistant","content":full_response})

    #大模型响应完后再次保存会话信息
    save_session()
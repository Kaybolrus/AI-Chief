
import flet as ft
import sqlite3, json, hashlib, datetime, re, asyncio, os
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-1.5-flash"

SYSTEM_PROMPT = """
Ты AI шеф. Отвечай строго JSON:
{
 "title":"",
 "ingredients":[],
 "steps":[],
 "nutrition":{},
 "tools":[],
 "tags":[]
}
"""

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL)

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("chef.db", check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS recipes (json TEXT, hash TEXT UNIQUE)")
    def save(self, r):
        h = hashlib.md5(json.dumps(r).encode()).hexdigest()
        try:
            self.conn.execute("INSERT INTO recipes VALUES (?,?)",(json.dumps(r),h))
            self.conn.commit()
        except: pass
        return h

def timers(s): return [int(x) for x in re.findall(r"\[t:(\d+)\]", s)]

class AI:
    def __init__(self):
        self.first=None
    def gen(self, txt, last=None):
        if not self.first: self.first=txt
        msgs=[{"role":"user","parts":[SYSTEM_PROMPT]},
              {"role":"user","parts":[self.first]}]
        if last: msgs.append({"role":"model","parts":[json.dumps(last)]})
        msgs.append({"role":"user","parts":[txt]})
        r=model.generate_content(msgs, generation_config={"response_mime_type":"application/json"})
        return json.loads(r.text)

def main(page: ft.Page):
    db, ai = DB(), AI()
    state={"r":None,"h":None}
    col=ft.Column(scroll="auto")

    async def run_timer(sec, txt):
        while sec>0:
            await asyncio.sleep(1)
            sec-=1
            m,s=divmod(sec,60)
            txt.value=f"{m:02}:{s:02}"
            page.update()

    def render(r):
        col.controls.clear()
        col.controls.append(ft.Text(r["title"],size=26))
        col.controls.append(ft.Text("Ингредиенты"))
        for i in r["ingredients"]:
            col.controls.append(ft.Text("• "+i))
        col.controls.append(ft.Text("Шаги"))
        for s in r["steps"]:
            row=ft.Row([ft.Text(s)])
            for t in timers(s):
                txt=ft.Text(f"{t}:00")
                btn=ft.ElevatedButton("⏱",on_click=lambda e,t=t,txt=txt: page.run_task(run_timer(t*60,txt)))
                row.controls.append(btn); row.controls.append(txt)
            col.controls.append(row)
        col.controls.append(ft.Row([
            ft.ElevatedButton("🚀",on_click=lambda e: ask("сделай быстрее")),
            ft.ElevatedButton("💰",on_click=lambda e: ask("сделай дешевле")),
            ft.ElevatedButton("🥗",on_click=lambda e: ask("сделай полезнее"))
        ]))
        page.update()

    def ask(t):
        r=ai.gen(t,state["r"])
        state["r"]=r
        state["h"]=db.save(r)
        render(r)

    inp=ft.TextField(label="Напиши рецепт или изменение")
    page.add(ft.Column([
        ft.Text("AI Chef Pro",size=30),
        inp,
        ft.Row([
            ft.ElevatedButton("Отправить",on_click=lambda e: ask(inp.value)),
            ft.ElevatedButton("Новый",on_click=lambda e: (state.update({"r":None}),col.controls.clear(),page.update()))
        ]),
        col
    ]))

ft.app(target=main)

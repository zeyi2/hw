#!/bin/python3

import json
from pathlib import Path
from typing import Dict, List
import tkinter as tk #^env
import tkinter.font as tkfont
from tkinter import ttk, messagebox

DATA_FILE = Path("students.json")
FIELDS = ("学号", "姓名", "性别", "宿舍", "电话")
MINW = {"学号": 80, "姓名": 110, "性别": 60, "宿舍": 120, "电话": 180}

class StudentManager:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._students: List[Dict[str, str]] = self._load()

    def _load(self) -> List[Dict[str, str]]:
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            out: List[Dict[str, str]] = []
            if isinstance(data, list):
                for x in data:
                    if isinstance(x, dict):
                        row = {k: str(x.get(k, "")).strip() for k in FIELDS}
                        if row["学号"]:
                            out.append(row)
            return out
        except (OSError, json.JSONDecodeError):
            return []

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._students, f, ensure_ascii=False, indent=4)

    def all(self) -> List[Dict[str, str]]:
        return list(self._students)

    def find_by_id(self, sid: str):
        sid = sid.strip()
        return next((x for x in self._students if x["学号"] == sid), None)

    def add(self, stu: Dict[str, str]) -> None:
        sid = stu.get("学号", "").strip()
        if not sid:
            raise ValueError("学号不能为空")
        if self.find_by_id(sid):
            raise ValueError("该学号已存在，添加失败！")
        for k in ("姓名", "宿舍", "电话"):
            if not str(stu.get(k, "")).strip():
                raise ValueError(f"{k}不能为空")
        g = stu.get("性别", "").strip()
        if g not in ("男", "女"):
            raise ValueError("性别输入无效，请输入'男'或'女'")
        row = {k: str(stu.get(k, "")).strip() for k in FIELDS}
        self._students.append(row); self._save()

class App(tk.Tk):
    def __init__(self, mgr: StudentManager) -> None:
        super().__init__()
        self.title("学生宿舍管理系统")
        self.geometry("780x480"); self.minsize(680, 440)
        self.mgr = mgr
        self._style(); self._menu(); self._notebook()

    def _style(self) -> None:
        self.style = ttk.Style(self)
        try: self.style.theme_use("clam")
        except: pass
        f = tkfont.nametofont("TkDefaultFont")
        rh = f.metrics("linespace") + 8
        self.style.configure("Treeview", font=f, rowheight=rh)
        self.style.configure("Treeview.Heading", font=f)

    def _menu(self) -> None:
        m = tk.Menu(self); fm = tk.Menu(m, tearoff=0)
        fm.add_command(label="退出", command=self.destroy)
        m.add_cascade(label="文件", menu=fm); self.config(menu=m)

    def _notebook(self) -> None:
        nb = ttk.Notebook(self); nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.tab_add, self.tab_q, self.tab_all = ttk.Frame(nb), ttk.Frame(nb), ttk.Frame(nb)
        nb.add(self.tab_add, text="添加学生信息")
        nb.add(self.tab_q, text="查询学生信息")
        nb.add(self.tab_all, text="显示所有学生")
        self._tab_add(self.tab_add); self._tab_query(self.tab_q); self._tab_all(self.tab_all)

    def _tab_add(self, root: ttk.Frame) -> None:
        f = ttk.Frame(root, padding=16); f.pack(fill=tk.BOTH, expand=True)
        self.v_add: Dict[str, tk.StringVar] = {k: tk.StringVar() for k in FIELDS}
        r = 0
        for k in ("学号", "姓名", "宿舍", "电话"):
            ttk.Label(f, text=f"请输入{k}:").grid(row=r, column=0, sticky="e", pady=6, padx=6)
            ttk.Entry(f, textvariable=self.v_add[k], width=32).grid(row=r, column=1, sticky="w", pady=6); r += 1
        ttk.Label(f, text="请输入性别(男/女):").grid(row=r, column=0, sticky="e", pady=6, padx=6)
        ttk.Combobox(f, textvariable=self.v_add["性别"], values=("男", "女"), width=30, state="readonly").grid(row=r, column=1, sticky="w", pady=6); r += 1
        b = ttk.Frame(f); b.grid(row=r, column=0, columnspan=2, pady=12)
        ttk.Button(b, text="添加", command=self._add).pack(side=tk.LEFT, padx=6)
        ttk.Button(b, text="清空", command=self._add_clear).pack(side=tk.LEFT, padx=6)
        self.msg_add = tk.StringVar(); ttk.Label(f, textvariable=self.msg_add, foreground="#666").grid(row=r+1, column=0, columnspan=2, sticky="w")
        f.columnconfigure(1, weight=1)

    def _add(self) -> None:
        try:
            data = {k: v.get().strip() for k, v in self.v_add.items()}
            for k in ("学号", "姓名", "宿舍", "电话"):
                if not data.get(k): raise ValueError(f"{k}不能为空")
            if data.get("性别") not in ("男", "女"): raise ValueError("性别输入无效，请输入'男'或'女'")
            self.mgr.add(data); self.msg_add.set("学生信息添加成功!")
            messagebox.showinfo("成功", "学生信息添加成功!"); self._refresh_tree()
        except ValueError as e:
            self.msg_add.set(str(e)); messagebox.showerror("错误", str(e))

    def _add_clear(self) -> None:
        for v in self.v_add.values(): v.set("")
        self.msg_add.set("")

    def _tab_query(self, root: ttk.Frame) -> None:
        f = ttk.Frame(root, padding=16); f.pack(fill=tk.BOTH, expand=True)
        self.q_sid = tk.StringVar()
        ttk.Label(f, text="请输入要查询的学号:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(f, textvariable=self.q_sid, width=32).grid(row=0, column=1, sticky="w", pady=6)
        ttk.Button(f, text="查询", command=self._query).grid(row=0, column=2, padx=6, pady=6)
        self.q_out = tk.Text(f, height=8, width=60, state="disabled")
        self.q_out.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=2, pady=8)
        f.columnconfigure(1, weight=1); f.rowconfigure(1, weight=1)

    def _query(self) -> None:
        x = self.mgr.find_by_id(self.q_sid.get().strip())
        self.q_out.configure(state="normal"); self.q_out.delete("1.0", tk.END)
        self.q_out.insert(tk.END, "查询结果：\n"+self._fmt(x) if x else "未找到该学号对应的学生\n")
        self.q_out.configure(state="disabled")

    def _tab_all(self, root: ttk.Frame) -> None:
        frm = ttk.Frame(root, padding=8); frm.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(frm, columns=FIELDS, show="headings")
        vsb = ttk.Scrollbar(frm, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frm, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew"); vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew"); frm.rowconfigure(0, weight=1); frm.columnconfigure(0, weight=1)
        for c in FIELDS:
            self.tree.heading(c, text=c); self.tree.column(c, anchor="center", stretch=True, width=100)
        btns = ttk.Frame(root, padding=(0,6,0,0)); btns.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(btns, text="刷新", command=self._refresh_tree).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="复制选中到剪贴板", command=self._copy).pack(side=tk.LEFT, padx=6)
        self._refresh_tree()

    def _refresh_tree(self) -> None:
        for iid in self.tree.get_children(): self.tree.delete(iid)
        for r in self.mgr.all(): self.tree.insert("", tk.END, values=tuple(r[k] for k in FIELDS))
        self._autosize()

    def _autosize(self) -> None:
        font = tkfont.nametofont("TkDefaultFont"); pad = 24
        w = {c: font.measure(c) for c in FIELDS}
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, "values")
            for c, v in zip(FIELDS, vals): w[c] = max(w[c], font.measure(str(v)))
        for c in FIELDS: self.tree.column(c, width=max(MINW.get(c,80), w[c]+pad), stretch=True)

    def _copy(self) -> None:
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("提示","请先选择一行"); return
        vals = self.tree.item(sel[0],"values")
        text = " | ".join(f"{k}: {v}" for k, v in zip(FIELDS, vals))
        self.clipboard_clear(); self.clipboard_append(text)
        messagebox.showinfo("已复制","选中学生信息已复制到剪贴板")

    @staticmethod
    def _fmt(x: Dict[str, str] | None) -> str:
        if not x: return ""
        return f"学号: {x['学号']}\n姓名: {x['姓名']}\n性别: {x['性别']}\n宿舍: {x['宿舍']}\n电话: {x['电话']}\n"

def main() -> None:
    app = App(StudentManager(DATA_FILE)); app.mainloop()

if __name__ == "__main__":
    main()

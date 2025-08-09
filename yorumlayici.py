import sys
import time
import re
import math

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Yorumlayıcının kullandığı değişkenler, listeler, fonksiyonlar ve modüller
variables = {}
lists = {}
functions = {}
classes = {}
modules = {
    # 'time' modülü için Türkçe karşılıklar
    "time": {"bekle": time.sleep},
    # 'math' modülü için Türkçe karşılıklar
    "math": {
        "pi": math.pi,
        "karekok": math.sqrt,
        "sinus": math.sin,
        "cosinus": math.cos,
        "tanjant": math.tan
    }
}

# Giriş fonksiyonu: Kullanıcıdan veri alır ve istenilen türe dönüştürmeyi dener.
def t_input(prompt, cast_type=str):
    val = input(prompt)
    try:
        return cast_type(val)
    except:
        print("[HATA] Geçersiz giriş, varsayılan olarak metin olarak alındı.")
        return val

# Argümanları ayrıştırmak için yardımcı fonksiyon
def parse_args(arg_str):
    if not arg_str.strip():
        return []
    # Tırnak içindeki virgülleri göz ardı ederek argümanları ayır
    parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', arg_str)
    args = []
    for p in parts:
        p = p.strip()
        # Metin (string) değerler
        if p.startswith('"') and p.endswith('"'):
            args.append(p[1:-1])
        # Float değerler
        elif re.match(r'^-?\d+\.\d+$', p):
            args.append(float(p))
        # Integer değerler
        elif p.isdigit() or (p.startswith('-') and p[1:].isdigit()):
            args.append(int(p))
        # Mantıksal (boolean) değerler
        elif p.lower() == 'doğru':
            args.append(True)
        elif p.lower() == 'yanlış':
            args.append(False)
        else:
            # Modül değişkenleri
            if '.' in p:
                mod_name, var_name = p.split('.', 1)
                if mod_name in modules and var_name in modules[mod_name]:
                    args.append(modules[mod_name][var_name])
                else:
                    args.append(None)
            # Normal değişkenler
            else:
                args.append(variables.get(p, None))
    return args

# İfadeleri değerlendiren fonksiyon (örn: 5 + 3, a > b)
def evaluate_expression(expr):
    try:
        temp_expr = str(expr).strip()
        temp_expr = temp_expr.replace('{', '').replace('}', '')
        temp_expr = temp_expr.replace('veya', 'or').replace('ve', 'and')
        temp_expr = temp_expr.replace('büyükse', '>').replace('küçükse', '<').replace('eşitse', '==')
        
        for var in variables:
            temp_expr = re.sub(r'\b{}\b'.format(re.escape(var)), str(variables[var]), temp_expr)
        
        for mod in modules:
            for var in modules[mod]:
                temp_expr = temp_expr.replace(f"{mod}.{var}", str(modules[mod][var]))

        return eval(temp_expr)
    except Exception as e:
        print(f"[HATA] İfade değerlendirme hatası: '{expr}' → {e}")
        return False

# Blokları (örn: eğer, tekrar) okuyan fonksiyon
def read_block(lines, i):
    block = []
    depth = 0
    start_index = i
    while i < len(lines):
        line = lines[i]
        if '{' in line:
            depth += 1
            if depth > 1 or i > start_index:
                block.append(line)
        elif '}' in line:
            depth -= 1
            if depth == 0:
                return block, i
            if depth >= 0:
                block.append(line)
        elif i > start_index:
             block.append(line)
        
        i += 1
    return block, i

# Kullanıcıdan giriş alma komutlarını işleyen fonksiyon
def handle_input(parts):
    cmd = parts[0]
    var_name = parts[1]
    if cmd == "oku":
        variables[var_name] = input(f"{var_name}: ")
    elif cmd == "oku_int":
        variables[var_name] = t_input(f"{var_name} (int): ", int)
    elif cmd == "oku_float":
        variables[var_name] = t_input(f"{var_name} (float): ", float)

# Dosya okuma/yazma işlemlerini yürüten fonksiyon
def handle_file(cmd, path, var_name=None):
    try:
        if cmd == "oku_dosya":
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if var_name:
                variables[var_name] = content
        elif cmd == "yaz_dosya":
            text = str(variables.get(var_name, ""))
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
    except Exception as e:
        print(f"[HATA] Dosya işlemi hatası: {e}")

# Sınıf örneği (instance) için yardımcı sınıf
class Instance:
    def __init__(self, cls_def):
        self.__dict__['__class__'] = cls_def
        for attr, val in cls_def.get('attributes', {}).items():
            self.__dict__[attr] = val
    
    def call(self, method, args):
        meth = self.__dict__['__class__']['methods'].get(method)
        if not meth:
            print(f"[HATA] Metod bulunamadı: {method}")
            return None
        local_vars = dict(zip(meth['params'], args))
        return run_block(meth['body'], local_vars)

# Kod bloklarını çalıştıran ana fonksiyon
def run_block(lines, local_vars=None):
    global variables, lists, functions, classes, modules

    old_vars = variables.copy()
    if local_vars:
        variables.update(local_vars)

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1
            continue

        func_match = re.match(r'^(\w+)\((.*)\)$', line)
        if func_match:
            cmd = func_match.group(1)
            args = parse_args(func_match.group(2))
        else:
            parts = re.split(r'\s+', line, maxsplit=3)
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []

        try:
            if cmd in ("oku", "oku_int", "oku_float"):
                handle_input(parts)
            elif cmd == 'yaz':
                outputs = []
                for arg in args:
                    outputs.append(variables.get(arg, arg))
                print(*outputs)
            elif cmd == 'sayıv':
                if len(parts) > 2 and parts[2] == '=':
                    var_name = parts[1]
                    expr = line.split('=',1)[1].strip()
                    variables[var_name] = evaluate_expression(expr)
                else:
                    variables[parts[1]] = 0
            
            elif cmd == 'hesapla':
                var_name = args[0]
                expr_str = ' '.join(args[2:])
                variables[var_name] = evaluate_expression(expr_str)
            
            elif cmd in ('oku_dosya', 'yaz_dosya'):
                handle_file(cmd, args[-1], args[0] if cmd == 'oku_dosya' else None)
            
            elif cmd == 'eğer':
                expr_str = line.split('eğer', 1)[1].strip()
                if not evaluate_expression(expr_str):
                    while i < len(lines) and not lines[i].strip().startswith('değilse'):
                        i += 1
            elif cmd == 'değilse':
                pass
            
            elif cmd == 'tekrar':
                count = int(variables.get(args[0], args[0]))
                block, jump = read_block(lines, i+1)
                for _ in range(count):
                    run_block(block)
                i = jump
            
            elif cmd == 'her_eleman_için':
                list_name = args[0]
                if list_name in lists:
                    block, jump = read_block(lines, i+1)
                    for item in lists[list_name]:
                        local_vars = {"_eleman": item}
                        run_block(block, local_vars)
                    i = jump
                else:
                    print(f"[HATA] Liste bulunamadı: {list_name}")
            
            elif cmd in modules['time']:
                if cmd == 'bekle':
                    seconds = variables.get(args[0], args[0])
                    modules['time']['bekle'](float(seconds))
            elif cmd in modules['math']:
                if cmd == 'pi':
                    print(modules['math']['pi'])
                else:
                    var_name, number = args[0], args[1]
                    func = modules['math'][cmd]
                    variables[var_name] = func(variables.get(number, number))
            
            elif cmd == 'metinv':
                m = re.search(r'"(.*)"', line)
                variables[args[0]] = m.group(1) if m else ''
            elif cmd == 'mantıksalv':
                variables[args[0]] = (args[-1] == True)
            elif cmd == 'listav':
                lists[args[0]] = []
            elif cmd == 'ekle':
                lst, val = args[0], args[1]
                lists[lst].append(variables.get(val, val))
            elif cmd == 'uzunluk':
                print(len(lists.get(args[0], [])))
            elif cmd == 'al':
                print(lists[args[0]][int(args[1])])

            elif cmd == 'işlev':
                name = args[0].split('(')[0]
                params_str = line[line.find('(')+1:line.rfind(')')]
                params = [p.strip() for p in params_str.split(',') if p.strip()]
                block, jump = read_block(lines, i+1)
                functions[name] = { 'params': params, 'body': block }
                i = jump
            elif cmd == 'dön':
                ret_val = variables.get(args[0], args[0])
                variables['_ret_'] = ret_val
                return ret_val
            elif cmd in functions:
                ret = run_block(functions[cmd]['body'], dict(zip(functions[cmd]['params'], args)))
                variables['_ret_'] = ret
            elif '.' in cmd:
                var_name, method_name = cmd.split('.', 1)
                obj = variables.get(var_name)
                if obj and isinstance(obj, Instance):
                    ret = obj.call(method_name, args)
                    variables['_ret_'] = ret
                else:
                    print(f"[HATA] '{var_name}' bir nesne değil veya metot '{method_name}' bulunamadı.")
            elif cmd in classes:
                inst = Instance(classes[cmd])
                variables[args[0]] = inst
            else:
                    print(f"[HATA] Tanımlanamayan komut: '{cmd}'")

        except Exception as e:
            print(f"[HATA] Satır {i+1}: {line} → {e}")

        i += 1
    
    if local_vars:
        variables = old_vars
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python yorumlayici.py dosya.turkcekod")
    else:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                main_lines = [re.split(r';|#', l)[0].strip() for l in f if l.strip()]
            run_block(main_lines)
        except FileNotFoundError:
            print(f"[HATA] Dosya bulunamadı: {sys.argv[1]}")

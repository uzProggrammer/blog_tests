import base64
import re
import mammoth, pprint


def get_html_content(docx):
    html_content = ''
    with open(docx, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html_content = result.value
    return html_content


def get_paragraphs_from_not_formatted_html(docx):
    reg = re.findall(r'<p(\s.*?)?>(.*?)</p>', get_html_content(docx), flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return reg



def to_dict_question(file):
    d = get_paragraphs_from_not_formatted_html(file)
    data = []
    true_answers = []
    balls = []
    start_answers = False
    for p in d:
        p = p[1]
        answers = []
        if not any(option in p for option in ["A)", "B)", "C)", "D)", "a)", "b)", "c)", "d)"]):
            if p.strip() == "Javoblar:":
                start_answers = True
                continue
            elif not start_answers and data and len(data[-1]['answers'])==0:
                data[-1]['question'] += p.strip()
            elif not start_answers:
                data.append({
                    "question": p.strip(),
                    "answers": []
                })
            elif start_answers:
                p = p.strip()
                p=p.split(')')
                true_answers.append(
                    p[1].split(',')[0].strip()
                )
                balls.append(
                    p[1].split(',')[1].strip()
                )
        if any(option in p for option in ["A)", "B)", "C)", "D)", "a)", "b)", "c)", "d)"]):
            i = 0
            if p.startswith("A)") and 'B)' not in p:
                data[-1]["answers"] = [p.strip()[2:]]
                continue
            elif p.startswith("B)") and 'C)' not in p:
                data[-1]['answers'].append(p.strip()[2:])
                continue
            if p.startswith("C)") and 'D)' not in p:
                data[-1]['answers'].append(p.strip()[2:])
                continue
            if p.startswith("D)")  and 'A)' not in p:
                data[-1]['answers'].append(p.strip()[2:])
                continue
            if p.startswith("a)")  and not 'b)' in p:
                data[-1]["answers"] = [p.strip()[2:]]
                continue
            elif p.startswith("b)")   and not 'c)' in p:
                data[-1]['answers'].append(p.strip()[2:])
                continue
            if p.startswith("c)")  and not 'b)' in p:
                data[-1]['answers'].append(p.strip()[2:])
                continue
            if p.startswith("d)")  and not 'b)' in p:
                data[-1]['answers'].append(p.strip()[2:])
                continue
            while p and len(answers) < 4  and i < len(p):
                if p and p[i] in ["A", "B", "C", "D", "a", "b", "c", "d"] and p[i + 1] == ")":                     
                    answers.append(p[:i].strip())
                    p = p[i+2:]
                    i = 0
                else:
                    i += 1
            answers.append(p.strip())
            
            answers = answers[1:]
            data[-1]['answers'] = answers
    return data, true_answers, balls
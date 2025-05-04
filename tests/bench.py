import json
from typing import List, Dict, Tuple, Any
import pandas as pd
from pydantic import BaseModel, Field
from mastodon_emulation import MastodonEmulator, typed_to_enum, StatusPost
from dataclasses import asdict


class EvaluationResult(BaseModel):
    relevance: int = Field(description="Оценка релевантности (балл 0-5)")
    style: int = Field(description="Оценка соответствия стилю (балл 0-5)")
    plausibility: int = Field(description="Оценка правдоподобности (балл 0-5)")


class MastodonBenchmark:
    def __init__(self, graph, profile, mastodon, llm):
        self.graph = graph
        self.profile = profile
        self.cases = []
        self.result_scores = []
        self.res_log = []
        self.mastodon = mastodon
        self.evaluator = llm  # Модель для LLM as a Judge

    def load_bench(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            non_typed = json.load(f)

            for case in non_typed:
                self.cases.append({
                    'input_signal': case['input_signal'],
                    'outputs': [typed_to_enum(i) for i in case['outputs']]
                })

    def simulate_notification(self, user: str, content: str, post_id: int) -> Dict:
        """Эмулирует упоминание от пользователя."""

        state = {
            'profile': self.profile,
            'context': {
                'text': content,
                'post_id': post_id,
                'is_mention': True,
                'user': user
            }
        }

        config = {"configurable": {"thread_id": user}, "recursion_limit": 8}

        return self.graph.invoke(state, config=config)

    def simulate_update(self, user: str, content: str, post_id: int) -> Dict:
        """Эмулирует упоминание от пользователя."""

        state = {
            'profile': self.profile,
            'context': {
                'text': content,
                'post_id': post_id,
                'is_mention': False,
                'user': user
            }
        }

        config = {"configurable": {"thread_id": user}, "recursion_limit": 8}

        return self.graph.invoke(state, config=config)

    def evaluate_text_output(self, history: List, gold_text: str, output_text: str) -> EvaluationResult:
        """Оценивает текстовый вывод с помощью LLM as a Judge."""

        prompt = f"""
        Оцени следующий ответ агента по трем критериям: релевантность, соответствие стилю и правдоподобность.
        История диалога: {history}
        Эталонный ответ: {gold_text}
        Ответ агента: {output_text}
        Профиль агента: {self.profile}
        """
        result = self.evaluator.with_structured_output(EvaluationResult).invoke(prompt)
        print(f'Оценка LLM:\n{result}\n')

        return (result.relevance + result.style + result.plausibility) / 3

    def score(self, state: Any, gold: List, real: List) -> float:
        n_text = 0

        real_texts = [a for a in real if str(a).startswith('StatusPost')]

        scores = []

        if not state.get('chat_history'):
            state['chat_history'] = []

        if not gold and real:
            return 0

        if not gold and not real:
            return 5

        for action in gold:
            if str(action).startswith('StatusPost') and real_texts:
                real_text = real_texts[n_text]
                score = self.evaluate_text_output(history=state['chat_history'], gold_text=action.content, output_text=real_text.content)
                scores.append(score)
                n_text += 1

            else:
                scores.append(5 if str(action) in str(real) else 0)

        return round(sum(scores) / len(scores), 2)

    def run(self) -> Dict:
        """Запускает бенчмарк для списка тестов."""

        for num, case in enumerate(self.cases):
            print('='*50 + '\n')
            print(f'Запускаю тест {num+1} / {len(self.cases)}:' + '\n')

            input_ = case['input_signal']
            print(f'Вводные:\n{input_}' + '\n')

            print(f'Эталонный ответ:\n{case["outputs"]}' + '\n')

            state = {}

            try:
                if input_['type'] == 'notification':
                    state = self.simulate_notification(**input_['args'])

                if input_['type'] == 'update':
                    state = self.simulate_update(**input_['args'])

            except:
                # import traceback
                # traceback.print_exc()
                pass

            results = self.mastodon.iteration_memory
            self.mastodon.step()

            print(f'Фактический ответ:\n{results}' + '\n')
            self.result_scores.append(self.score(state=state, gold=case['outputs'], real=results))

            print(f'Итоговая оценка за кейс: {self.result_scores[-1]}' + '\n')

            self.res_log.append({'input_signal': input_, 'gold_outputs': [asdict(r) for r in case['outputs']], 'real_outputs': [asdict(r) for r in results], 'score': self.result_scores[-1]})

        final_mark = sum(self.result_scores) / len(self.result_scores)
        print('\n' * 2 + '=' * 50 + '\n' * 2)
        print(f'Итоговая оценка за бенчмарк: {final_mark}')

        with open('results/bench_res.json', 'w', encoding='utf-8') as f:
            json.dump(self.res_log, f, ensure_ascii=False, indent=2)

        pd.DataFrame(self.res_log).to_csv('results/bench_res.csv', index=False)


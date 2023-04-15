import os
import openai
import random
import re
openai.api_key = os.getenv("OPENAI_API_KEY")

def find_weight(text) -> list:
    
    pattern = r'\[([^\]]+)\]'
    result = re.search(pattern, text)

    if result:
        values = result.group(1)
        
        print(values)
    else:
        print("No match found")
    return list(eval(values))

def generate_text(options):
    my_list = [i for i in range(len(options))]
    random.shuffle(my_list)
    text=f'weight={str(my_list)}'
    return text


import random

# 플레이어 클래스
class Player:
    def __init__(self, name):
        print(f'플레이어 {name} 생성중...')
        self.name = name
        # self.role = role
        self.alive = True
        self.vote = None
        self.votes_received = 0   # 투표 수를 기록하기 위한 변수 추가 시민 중 하나
        self.messages=[{"role": "user", "content": f"너는 IQ180의 천재적인 두뇌를 가진 탐정이야. 현재 마피아 게임에 참가하고 있어. 앞으로 마피아게임을 진행하면서 낮에는 토론을 통해 마피아를 찾고 밤에는 역할을 부여받았을 경우 주어진 역할에 충실해야해.  \
          그리고 아래와 같은 양식을 지켜줘 \n'{self.name}: 네가 하고싶은 말'"}]

    def is_alive(self):
        return self.alive
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def die(self):
        '''
        플레이어를 죽이는 함수
        '''
        self.alive = False
    
    def set_vote(self, player):
        '''
        플레이어가 투표한 대상을 설정하는 함수
        '''
        self.vote = player


    def vote_count(self):
        '''
        플레이어가 받은 투표 수를 반환하는 함수
        '''
        return self.votes_received

    
    def think(self, text, speak=None):
        '''
        # GPT-3.5로 플레이어의 생각을 처리하고, 필요한 경우 응답을 출력하는 함수
        '''
        self.messages.append({"role": "user", "content": f"{text}"})
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages,temperature=1)
        assistant_content = completion.choices[0].message["content"].strip()
        if speak == 'speak':
            print(assistant_content)
        
        return assistant_content





# 게임 클래스
class MafiaGame(Player):
    def __init__(self, players):
        
        self.players = players
        
        self.roles = ["마피아", "경찰", "의사", "시민"]
        self.mafia = None
        self.police = None
        self.doctor = None
        self.num_days = 0
        self.num_mafia = 0
        self.num_citizen = 0
        # self.messages2=[]
    def add_message(self,text,role):
        '''
        플레이어에게 메시지를 전달하는 함수. 
        '''
    
        if role == '마피아':

            self.mafia.messages.append({"role": "user", "content": text})
        elif role == '경찰':
            self.police.messages.append({"role": "user", "content": text})
        elif role == '의사':
            self.doctor.messages.append({"role": "user", "content": text})
        
        elif role == '사회자':
            print(text)
            for player in self.players:
                player.messages.append({"role": "user", "content": text})
        
    
    def set_roles(self):
        '''
        게임의 역할을 지정하는 함수

        '''
        
        num_players = len(self.players)
        print('마피아 1명을 뽑는중...')
        self.mafia = random.choice(self.players)
        self.mafia.role = "마피아"
        self.mafia.think('당신은 마피아입니다. 뛰어난 연기력을 바탕으로 시민들을 속이세요. 당신은 경찰이나 의사를 사칭할수도 있습니다. 밤이되면 죽을 시민을 선택할 수 있습니다.')
        print('경찰 1명을 뽑는중...')
        self.police = random.choice([p for p in self.players if p is not self.mafia])
        self.police.role = "경찰"
        self.police.think("당신은 경찰입니다. 밤이되면 한 명을 지목하여 마피아 여부를 확인할 수 있습니다. 낮의 대화를 통해서 마피아를 추론해야합니다. 경찰은 수사를 통해 알게된 사실을 공유하며 시민을 자신의 편으로 만들수도 있습니다.")
        print('의사 1명을 뽑는중...')
        self.doctor = random.choice([p for p in self.players if p is not self.mafia and p is not self.police])
        self.doctor.role = "의사"
        self.doctor.think("당신은 의사입니다. 밤이되면 한 명을 지목하여 치료할 수 있습니다. 이때 자기자신을 선택할수도 있습니다. 마피아가 죽일만한 시민을 선택하여 치료하세요.")
        self.num_mafia = 1
        self.num_citizen = num_players - self.num_mafia 
        
        # 나머지 플레이어들은 시민으로 설정
        for p in self.players:
            if p is not self.mafia and p is not self.police and p is not self.doctor:
                p.role = "시민"
                p.think('당신은 시민입니다. 마피아로 의심되는 사람을 대화내용, 투표 등을 분석하여 찾아야합니다. 2일차, 3일차가 되면 마피아로 의심되는 사람을 말하고 그 이유도 설명해야합니다.')
                
    
    def play_game(self):
        while True:
            self.num_days += 1
            self.day()
            if self.is_game_over():
                break
            self.night()
            if self.is_game_over():
                break
            
    
    def is_game_over(self):

        if self.num_mafia == 0:
            print("모든 마피아가 죽었습니다. 시민팀이 승리했습니다!")
            # self.add_message("모든 마피아가 죽었습니다. 시민팀이 승리했습니다!", '사회자')
            print("마피아: ", [p.name for p in self.players if p.role == "마피아"])
            print("경찰: ", [p.name for p in self.players if p.role == "경찰"])
            print("의사: ", [p.name for p in self.players if p.role == "의사"])
            return True
        elif self.num_mafia >= self.num_citizen:
            print("마피아의 수가 시민의 수와 같거나 많아졌습니다. 마피아팀이 승리했습니다!")
            # self.add_message("마피아의 수가 시민의 수와 같거나 많아졌습니다. 마피아팀이 승리했습니다!", '사회자')
            print("마피아: ", [p.name for p in self.players if p.role == "마피아"])
            print("경찰: ", [p.name for p in self.players if p.role == "경찰"])
            print("의사: ", [p.name for p in self.players if p.role == "의사"])
            return True
        return False

    def night(self):
        victim = None  # 변수 초기화
        saved = None
        print("=========================================")
        self.add_message("밤이 되었습니다.",'사회자')
        print("=========================================")
        for player in self.players:
            if player.role == "마피아" and player.alive:
                victim = self.mafia_kill()
            elif player.role == "경찰" and player.alive:
                self.police_investigate()
            elif player.role == "의사" and player.alive:
                saved = self.doctor_save()

        if victim is not None and victim != saved:
            victim.die()
            self.add_message(f"{victim.name}이(가) 마피아에게 죽었습니다.",'사회자')
            
            if victim.role == "마피아":
                self.num_mafia -= 1
            else:
                self.num_citizen -= 1
        else:
            self.add_message("의사의 치료 덕분에 오늘 밤 아무도 죽지 않았습니다.", '사회자')

    def mafia_kill(self):
        self.add_message("마피아는 죽일 사람을 선택해주세요.", '사회자')
        victims = [p for p in self.players if p.alive and p is not self.mafia]
        
        if isinstance(self.mafia, HumanPlayer):
            text = input(f"다음 플레이어 목록에서 마피아가 밤에 죽일것 같은 플레이어를 순서대로 가중치를 할당해주세요. \
            가중치 값은 정수여야 하며, 목록에 있는 플레이어 수와 일치해야 합니다. 아래 양식에 맞춰 가중치 리스트를 작성해주세요. 예: [1, 2, 3]\n투표 대상: {victims}")
        else:
            try:
                text = self.mafia.think(f"다음 플레이어 목록에서 마피아가 밤에 죽일것 같은 플레이어를 순서대로 가중치를 할당해주세요. \
                가중치 값은 정수여야 하며, 목록에 있는 플레이어 수와 일치해야 합니다. 아래 양식에 맞춰 가중치 리스트를 작성해주세요. 예: [1, 2, 3]\n투표 대상: {victims}")
            except:
                text = generate_text(victims)
        print(1,text)
        try:
            weights = find_weight(text)
            victim = random.choices(victims, weights)[0]
        except:
            victim = random.choices(victims)
        return victim
            
    def doctor_save(self):
        self.add_message("의사는 조용히 일어나 한 명을 지목해주세요.",'사회자')

        patients = [p for p in self.players if p.alive and p is not self.doctor]
        if isinstance(self.doctor, HumanPlayer):
            text = input(f"다음 플레이어 목록에서 마피아가 밤에 죽일것 같은 플레이어를 순서대로 가중치를 할당해주세요. \
            가중치 값은 정수여야 하며, 목록에 있는 플레이어 수와 일치해야 합니다. 아래 양식에 맞춰 가중치 리스트를 작성해주세요. 예: [1, 2, 3]\n투표 대상: {patients}")
        else:
            try:
                text = self.doctor.think(f"다음 플레이어 목록에서 마피아가 밤에 죽일것 같은 플레이어를 순서대로 가중치를 할당해주세요. \
                가중치 값은 정수여야 하며, 목록에 있는 플레이어 수와 일치해야 합니다. 아래 양식에 맞춰 가중치 리스트를 작성해주세요. 예: [1, 2, 3]\n투표 대상: {patients}")
            except:
                text = generate_text(patients)
        print(2,text)
        try:
            weights = find_weight(text)
            patient = random.choices(patients, weights)[0]
        except:
            patient = random.choices(patients)

        if patient.alive:
            self.add_message(f"의사는 {patient.name}을(를) 치료했습니다.",'의사')
        else:
            self.add_message(f"{patient.name}은(는) 이미 죽었습니다.",'의사')

        return patient
    def police_investigate(self):
        self.add_message("경찰은 조용히 일어나 한 명을 지목해주세요.",'사회자')
        suspects = [p for p in self.players if p.alive and p is not self.police]

        if isinstance(self.police, HumanPlayer):    
            text = input(f"다음 플레이어 목록에서 마피아로 의심되는 순서대로 가중치를 할당해주세요. \
            가중치 값은 정수여야 하며, 목록에 있는 플레이어 수와 일치해야 합니다. 아래 양식에 맞춰 가중치 리스트를 작성해주세요. 예: [1, 2, 3]\n투표 대상: {suspects}")
        else:
            try:
                text = self.police.think(f"다음 플레이어 목록에서 마피아로 의심되는 순서대로 가중치를 할당해주세요. \
                가중치 값은 정수여야 하며, 목록에 있는 플레이어 수와 일치해야 합니다. 아래 양식에 맞춰 리스트를 작성해주세요. 예: [1, 2, 3]\n투표 대상: {suspects}")
            except:
                text = generate_text(suspects)
        print(3,text)
        try:
            weights = find_weight(text)
            suspect = random.choices(suspects, weights)[0]
        except:
            suspect = random.choices(suspects)
        # suspect = self.police.choose(suspects)
        if suspect.role == "마피아":
            self.add_message(f"{suspect.name}은(는) 마피아입니다.",'경찰')
        else:
            self.add_message(f"{suspect.name}은(는) 시민입니다.",'경찰')


    def day(self):
        alives = [p for p in self.players if p.alive ]
        print("=========================================")
        self.add_message(f"낮이 되었습니다.  <{self.num_days}일차> \n생존자: {alives} \n낮 시간동안 자유롭게 대화를 나눠주세요.",'사회자')
        print("=========================================")
        for player in self.players:
            if player.alive:
                self.add_message(f'{player.name}님, 발언해주세요.','사회자')
                speak = player.think('당신의 발언차례입니다. 자유롭게 의견을 말해주세요.')
                self.add_message(speak,'사회자')
                print('-------------------------------------')
        candidate = self.vote()
        
        
        candidate.die()
        if candidate.role == "마피아":
            self.add_message(f"마피아 {candidate.name}님께서 죽었습니다.",'사회자')
            self.num_mafia -= 1
        else:
            self.add_message(f"선량한 시민 {candidate.name}님께서 죽었습니다.",'사회자')
            self.num_citizen -= 1

    def vote(self):
        vote = None
        self.add_message(">>> 투표를 시작합니다", "사회자")

        alive_players = [p for p in self.players if p.alive]

        # 각 플레이어의 투표 수를 저장하는 딕셔너리 생성
        vote_counts = {p: 0 for p in alive_players}

        for player in alive_players:
            vote_players = []
            print(f"{player.name}님, 누구에게 투표하시겠습니까?")
            # self.add_message(f"{player.name}님, 누구에게 투표하시겠습니까?", "사회자")
            for p in alive_players:
                if p is not player:
                    vote_players.append(p)
                    print(f"{p.name}: {vote_counts[p]}표")  # 각 플레이어의 투표 수를 출력
            while True:
                vote_players_name = [p.name for p in vote_players]
                if isinstance(player, HumanPlayer):
                    text = input(f"다음 플레이어 목록에서 마피아로 의심되는 순서대로 가중치를 할당해주세요. \
                    가중치 값은 정수여야 하며, 목록에 있는 플레이어 수와 일치해야 합니다. 아래 양식에 맞춰 정확한 가중치 리스트를 작성해주세요. 예: [1, 2, 3]\n투표 대상: {vote_players_name}")
                else:
                    try:
                        text = player.think(f"다음 플레이어 목록에서 마피아로 의심되는 순서대로 가중치를 할당해주세요. \
                        가중치 값은 정수여야 하며, 목록에 있는 플레이어 수와 일치해야 합니다. 아래 양식에 맞춰 'weight=' 다음에 정확한 가중치 리스트를 작성해주세요. 예: weight=[1, 2, 3]\n투표 대상: {vote_players_name}")
                    except:
                        text=generate_text(vote_players_name)
              

                    
                print('투표',text)
                weights = find_weight(text)
                vote = random.choices(vote_players, weights)[0]
                self.add_message(f"{player.name}님은 {vote}님에게 투표했습니다.", "사회자")
                candidate = next((p for p in alive_players if p.name == str(vote)), None)
                if candidate:
                    player.set_vote(candidate)
                    vote_counts[candidate] += 1  # 해당 플레이어의 투표 수를 1 증가시킴
                    break
                else:
                    print("잘못된 이름입니다. 다시 입력해주세요.")
        candidate_votes = {p: 0 for p in alive_players}
        for player in alive_players:
            candidate_votes[player.vote] += 1

        # 투표 결과 출력
        candidate = max(candidate_votes, key=candidate_votes.get)
        self.add_message(f"{candidate.name}님이 가장 많은 표를 얻었습니다", "사회자")

        # 최후의 변론
        self.final_defense(candidate)
        return candidate


        
    def final_defense(self, candidate):
        self.add_message(f"{candidate.name}님, 최후의 변론을 해주세요.", "사회자")
        defense = candidate.think("당신은 처형 후보입니다. 만약 주어진 역할이 경찰이나 의사라면 \
        자신의 역할을 말해주세요. 최후의 변론을 통해 마피아가 아님을 주장해보세요.")
        self.add_message(defense, "사회자")


class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)


    def think(self, text, speak=None):
        '''
        실제 인간 플레이어의 생각을 표현하는 함수
        '''
        text=input(f'{text}: ')

        if speak == 'speak':
            print(text)
        
        return text


your_name=input('당신의 이름을 입력하세요:')
# 플레이어 생성
player1 = Player("나연")
player2 = Player("정연")
player3 = Player("사나")
player4 = Player("미나")
player5 = Player("모모")
player6 = HumanPlayer(your_name)

# 게임 생성
game = MafiaGame([player1, player2, player3, player4, player5, player6])

# 역할 지정
game.set_roles()

# 게임 진행
game.play_game()



#Importação das libs
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CONN, Pessoa, Tokens
from secrets import token_hex
import re

#Criação da instância do fastapi
app = FastAPI()

#Criação da função de conexão com bd
def conectBD():
    engine = create_engine(CONN, echo=True)
    Session = sessionmaker(bind=engine)
    return Session()

#Criação da url para cadastro mais funcão
@app.post('/cadastro')
def cadastro(nome: str, user: str, senha: str):
    session = conectBD()
    usuario = session.query(Pessoa).filter_by(usuario=user).all()
    
    if len(usuario) > 0:
        return {'status': 'Usuário já cadastrado'}
    
    if (validaSenha(senha) != True):
        return {'status': f'{validaSenha(senha)}'}

    if len(usuario) == 0:
        x = Pessoa(nome=nome, usuario=user,senha=senha)
        session.add(x)
        session.commit()
        return {'status': 'Sucesso'}
   

@app.post('/login')
def login(user: str, senha: str):
    session = conectBD()
    usuario = session.query(Pessoa).filter_by(usuario=user).all()
    
    if len(usuario) == 0:
        return {'status': 'Usuário inexistente'}
    
    if (usuario[0].senha != senha):
        return {'status': 'Senha incorreta'}


    while True:
        token = token_hex(50)
        tokenExiste = session.query(Tokens).filter_by(token=token).all()
        
        if len(tokenExiste) == 0:
            pessoaExiste = session.query(Tokens).filter_by(id_pessoa=usuario[0].id).all()
            
            if len(pessoaExiste) == 0:
                novoToken = Tokens(id_pessoa=usuario[0].id, token=token)
                session.add(novoToken)
            
            elif len(pessoaExiste) > 0:
                pessoaExiste[0].token = token

            session.commit()
            break
    return token

#Validação senha
def validaSenha(senha):
    mensagem = ''
    if(len(senha)< 6):
        mensagem = 'A senha deve possuir no minimo 6 caracteres'
        return mensagem
    elif(len(senha)>14):
        mensagem = 'A senha deve possuir no maximo 14 caracteres'
        return mensagem
    elif not (re.search("[A-Z]", senha)):
        mensagem = 'A senha não contem letra maiúsculas'
        return mensagem
    elif re.search("\s", senha): 
        mensagem = 'A senha contem espacos em branco'
        return mensagem
    else:
        return True
        
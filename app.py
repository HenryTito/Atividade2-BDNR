from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client.mercadolivre

def delete_usuario(nome, sobrenome):
    mycol = db.usuario
    myquery = {"nome_usuario": nome, "sobrenome_usuario": sobrenome}
    result = mycol.delete_one(myquery)
    print("Usuário deletado!" if result.deleted_count else "Usuário não encontrado.")

def create_usuario():
    mycol = db.usuario
    print("\nInserindo um novo usuário")
    nome = input("Nome: ")
    sobrenome = input("Sobrenome: ")
    cpf = input("CPF: ")
    email = input("Email: ")
    senha = input("Senha: ")

    enderecos = []

    while True:
        rua = input("Rua: ")
        num = input("Número: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        estado = input("Estado: ")
        cep = input("CEP: ")

        endereco = {
            "rua": rua,
            "numero": num,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "cep": cep
        }

        enderecos.append(endereco)

        key = input("Deseja adicionar outro endereço (S/N)? ").upper()
        if key == 'N':
            break

    usuario = {
        "nome_usuario": nome,
        "sobrenome_usuario": sobrenome,
        "cpf_usuario": cpf,
        "email_usuario": email,
        "senha_usuario": senha,
        "enderecos": enderecos,
        "favoritos": []
    }

    x = mycol.insert_one(usuario)
    print("Usuário inserido com ID", x.inserted_id)

def add_favorito(email_usuario, nome_produto):
    usuarios = db.usuario
    produtos = db.produto

    usuario = usuarios.find_one({"email_usuario": email_usuario})
    if not usuario:
        print("Usuário não encontrado!")
        return

    produto = produtos.find_one({"nome_produto": nome_produto})
    if not produto:
        print("Produto não encontrado!")
        return

    favorito = {
        "id_produto": str(produto["_id"]),
        "nome_produto": produto["nome_produto"]
    }

    favoritos = usuario.get("favoritos", [])
    ja_existe = any(
        (
            isinstance(item, dict)
            and item.get("id_produto") == favorito["id_produto"]
        )
        or item == nome_produto
        for item in favoritos
    )
    if ja_existe:
        print("Produto já está na lista de favoritos.")
        return

    usuarios.update_one(
        {"_id": usuario["_id"]},
        {"$addToSet": {"favoritos": favorito}}
    )
    print("Favorito adicionado com sucesso!")

def listar_favoritos(email_usuario):
    usuario = db.usuario.find_one({"email_usuario": email_usuario})

    if not usuario:
        print("Usuário não encontrado!")
        return

    favoritos = usuario.get("favoritos", [])
    if not favoritos:
        print("Usuário não possui favoritos cadastrados.")
        return

    print("Favoritos do usuário:")
    for favorito in favoritos:
        if isinstance(favorito, dict):
            print(f"ID: {favorito.get('id_produto')} | Nome: {favorito.get('nome_produto')}")
        else:
            print(f"Nome: {favorito}")

def remover_favorito(email_usuario, nome_produto):
    usuarios = db.usuario
    produtos = db.produto
    usuario = usuarios.find_one({"email_usuario": email_usuario})

    if not usuario:
        print("Usuário não encontrado!")
        return

    produto = produtos.find_one({"nome_produto": nome_produto})
    favorito_dict = None
    if produto:
        favorito_dict = {
            "id_produto": str(produto["_id"]),
            "nome_produto": produto["nome_produto"]
        }

    favoritos = usuario.get("favoritos", [])
    existe = any(
        (
            isinstance(item, dict)
            and (
                (favorito_dict and item.get("id_produto") == favorito_dict["id_produto"])
                or item.get("nome_produto") == nome_produto
            )
        )
        or item == nome_produto
        for item in favoritos
    )
    if not existe:
        print("Produto não está na lista de favoritos.")
        return

    pull_conditions = [nome_produto, {"nome_produto": nome_produto}]
    if favorito_dict:
        pull_conditions.append(favorito_dict)

    usuarios.update_one(
        {"_id": usuario["_id"]},
        {"$pull": {"favoritos": {"$in": pull_conditions}}}
    )
    print("Favorito removido com sucesso!")

def read_usuario(nome):
    mycol = db.usuario

    if not nome:
        for x in mycol.find().sort("nome_usuario"):
            print(x["nome_usuario"], x["cpf_usuario"])
    else:
        for x in mycol.find({"nome_usuario": nome}):
            print(x)

def update_usuario(nome):
    mycol = db.usuario

    usuario = mycol.find_one({"nome_usuario": nome})

    if not usuario:
        print("Usuário não encontrado!")
        return

    print("Dados atuais:", usuario)

    novo_nome = input("Novo nome: ")
    if novo_nome:
        usuario["nome_usuario"] = novo_nome

    novo_cpf = input("Novo CPF: ")
    if novo_cpf:
        usuario["cpf_usuario"] = novo_cpf

    mycol.update_one({"_id": usuario["_id"]}, {"$set": usuario})
    print("Usuário atualizado!")

def create_vendedor():
    mycol = db.vendedor

    nome = input("Nome: ")
    cpf = input("CPF: ")
    cnpj = input("CNPJ: ")

    vendedor = {
        "nome_vendedor": nome,
        "cpf_vendedor": cpf,
        "cnpj": cnpj,
        "produtos": [],
        "vendas": []
    }

    x = mycol.insert_one(vendedor)
    print("Vendedor inserido:", x.inserted_id)

def read_vendedor(nome):
    mycol = db.vendedor

    if not nome:
        for x in mycol.find():
            print(x["_id"], x["nome_vendedor"])
    else:
        for x in mycol.find({"nome_vendedor": nome}):
            print(x)

def update_vendedor():
    mycol = db.vendedor
    id = input("ID: ")

    vendedor = mycol.find_one({"_id": ObjectId(id)})

    if not vendedor:
        print("Não encontrado!")
        return

    nome = input("Novo nome: ")
    if nome:
        vendedor["nome_vendedor"] = nome

    mycol.update_one({"_id": vendedor["_id"]}, {"$set": vendedor})
    print("Atualizado!")

def delete_vendedor():
    mycol = db.vendedor
    id = input("ID: ")

    result = mycol.delete_one({"_id": ObjectId(id)})
    print("Deletado!" if result.deleted_count else "Não encontrado!")

def create_produto():
    mycol = db.produto

    produto = {
        "nome_produto": input("Nome: "),
        "descricao_produto": input("Descrição: "),
        "categoria": input("Categoria: "),
        "preco_produto": float(input("Preço: ")),
        "estoque_produto": int(input("Estoque: ")),
        "foto_produto": input("URL: "),
        "vendedor_produto": input("Vendedor: ")
    }

    x = mycol.insert_one(produto)
    print("Produto inserido:", x.inserted_id)

def read_produto(nome):
    mycol = db.produto

    if not nome:
        for x in mycol.find().sort("nome_produto"):
            print(x["_id"], x["nome_produto"])
    else:
        for x in mycol.find({"nome_produto": nome}):
            print(x)

def update_produto():
    mycol = db.produto
    id = input("ID: ")

    produto = mycol.find_one({"_id": ObjectId(id)})

    if not produto:
        print("Não encontrado!")
        return

    nome = input("Novo nome: ")
    if nome:
        produto["nome_produto"] = nome

    mycol.update_one({"_id": produto["_id"]}, {"$set": produto})
    print("Atualizado!")

def delete_produto(nome):
    mycol = db.produto
    result = mycol.delete_one({"nome_produto": nome})
    print("Deletado!" if result.deleted_count else "Não encontrado!")

def create_venda():
    mycol = db.venda

    venda = {
        "produto_nome": input("Produto: "),
        "usuario_nome": input("Usuário: "),
        "vendedor_nome": input("Vendedor: "),
        "valor": float(input("Valor: ")),
        "quantidade": int(input("Quantidade: ")),
        "data_compra": input("Data: "),
        "status": input("Status: ")
    }

    x = mycol.insert_one(venda)
    print("Venda inserida:", x.inserted_id)

def read_venda():
    for x in db.venda.find():
        print(x)

def update_venda():
    mycol = db.venda
    id = input("ID: ")

    venda = mycol.find_one({"_id": ObjectId(id)})

    if not venda:
        print("Não encontrada!")
        return

    status = input("Novo status: ")
    if status:
        venda["status"] = status

    mycol.update_one({"_id": venda["_id"]}, {"$set": venda})
    print("Atualizada!")

def delete_venda():
    mycol = db.venda
    id = input("ID: ")

    result = mycol.delete_one({"_id": ObjectId(id)})
    print("Deletada!" if result.deleted_count else "Não encontrada!")

while True:
    print("\n1-Usuário | 2-Vendedor | 3-Produto | 4-Venda | S-Sair")
    op = input("Opção: ").upper()

    if op == 'S':
        break

    if op == '1':
        sub = input("1-Criar 2-Ler 3-Atualizar 4-Deletar 5-Adicionar favorito 6-Listar favoritos 7-Remover favorito: ")
        if sub == '1':
            create_usuario()
        elif sub == '2':
            read_usuario(input("Nome: "))
        elif sub == '3':
            update_usuario(input("Nome: "))
        elif sub == '4':
            delete_usuario(input("Nome: "), input("Sobrenome: "))
        elif sub == '5':
            add_favorito(input("Email do usuário: "), input("Nome do produto: "))
        elif sub == '6':
            listar_favoritos(input("Email do usuário: "))
        elif sub == '7':
            remover_favorito(input("Email do usuário: "), input("Nome do produto: "))

    elif op == '2':
        sub = input("1-Criar 2-Ler 3-Atualizar 4-Deletar: ")
        if sub == '1':
            create_vendedor()
        elif sub == '2':
            read_vendedor(input("Nome: "))
        elif sub == '3':
            update_vendedor()
        elif sub == '4':
            delete_vendedor()

    elif op == '3':
        sub = input("1-Criar 2-Ler 3-Atualizar 4-Deletar: ")
        if sub == '1':
            create_produto()
        elif sub == '2':
            read_produto(input("Nome: "))
        elif sub == '3':
            update_produto()
        elif sub == '4':
            delete_produto(input("Nome: "))

    elif op == '4':
        sub = input("1-Criar 2-Ler 3-Atualizar 4-Deletar: ")
        if sub == '1':
            create_venda()
        elif sub == '2':
            read_venda()
        elif sub == '3':
            update_venda()
        elif sub == '4':
            delete_venda()

print("Adeus!")
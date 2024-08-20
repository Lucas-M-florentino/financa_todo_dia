<template>
    <form @submit.prevent="emitirTransacao" class="transacao-form">
      <h2>Adicionar Transação</h2>
  
      <div class="input-group">
        <label for="descricao">Descrição:</label>
        <input
          v-model="transacao.descricao"
          type="text"
          id="descricao"
          placeholder="Ex: Mercado"
          required
        />
      </div>
  
      <div class="input-group">
        <label for="valor">Valor:</label>
        <input
          v-model.number="transacao.valor"
          type="number"
          id="valor"
          placeholder="Ex: 100"
          required
        />
      </div>
  
      <div class="input-group">
        <label for="tipo">Tipo:</label>
        <select v-model="transacao.tipo" id="tipo">
          <option value="despesa">Despesa</option>
          <option value="receita">Receita</option>
        </select>
      </div>
  
      <button type="submit" class="btn-submit">Adicionar Transação</button>
    </form>
  </template>
  
  <script>
  export default {
    data() {
      return {
        transacao: {
          descricao: '',
          valor: 0,
          tipo: 'despesa'
        }
      }
    },
    methods: {
      emitirTransacao() {
        this.$emit('adicionarTransacao', this.transacao)
        // Resetando o formulário
        this.transacao = { descricao: '', valor: 0, tipo: 'despesa' }
      }
    }
  }
  </script>
  
  <style scoped>
  .transacao-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
    background-color: #f9f9f9;
  }
  
  .input-group {
    display: flex;
    flex-direction: column;
  }
  
  input,
  select {
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #ccc;
  }
  
  .btn-submit {
    padding: 10px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  
  .btn-submit:hover {
    background-color: #218838;
  }
  </style>
  
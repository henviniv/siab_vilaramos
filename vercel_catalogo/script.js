const modulos = [
  {
    titulo: 'Plano de estudos guiado',
    descricao: 'Cronograma estratégico com metas semanais para acelerar sua aprovação.'
  },
  {
    titulo: 'Aulas atualizadas',
    descricao: 'Conteúdos gravados com foco nos principais editais da sua área.'
  },
  {
    titulo: 'Mentorias ao vivo',
    descricao: 'Tire dúvidas em encontros quinzenais com professores especializados.'
  },
  {
    titulo: 'Simulados e correções',
    descricao: 'Pratique com questões comentadas e relatórios de desempenho.'
  }
];

const depoimentos = [
  {
    nome: 'Marina R.',
    texto: 'Consegui organizar minha rotina e fui aprovada em 5 meses.'
  },
  {
    nome: 'Carlos M.',
    texto: 'Os simulados ajudaram muito no meu desempenho final.'
  },
  {
    nome: 'Bianca A.',
    texto: 'Didática excelente e suporte rápido durante toda a preparação.'
  }
];

const planos = [
  {
    nome: 'Essencial',
    preco: 'R$ 97/mês',
    texto: 'Ideal para começar com base forte.',
    destaque: false
  },
  {
    nome: 'Aprovação',
    preco: 'R$ 147/mês',
    texto: 'Plano mais escolhido, com mentorias e simulados.',
    destaque: true
  },
  {
    nome: 'Premium',
    preco: 'R$ 197/mês',
    texto: 'Inclui análise individual e plano personalizado.',
    destaque: false
  }
];

function render() {
  const modulosEl = document.getElementById('cards-modulos');
  const depoimentosEl = document.getElementById('cards-depoimentos');
  const planosEl = document.getElementById('cards-planos');

  modulos.forEach((item) => {
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `<h3>${item.titulo}</h3><p>${item.descricao}</p>`;
    modulosEl.appendChild(card);
  });

  depoimentos.forEach((item) => {
    const card = document.createElement('article');
    card.className = 'testimonial';
    card.innerHTML = `<p>“${item.texto}”</p><strong>${item.nome}</strong>`;
    depoimentosEl.appendChild(card);
  });

  planos.forEach((item) => {
    const card = document.createElement('article');
    card.className = `price-card ${item.destaque ? 'price-card--highlight' : ''}`;
    card.innerHTML = `
      <h3>${item.nome}</h3>
      <div class="price">${item.preco}</div>
      <p>${item.texto}</p>
      <a class="btn btn--primary" href="#">Assinar agora</a>
    `;
    planosEl.appendChild(card);
  });
}

render();

document.addEventListener('DOMContentLoaded', () => {
    const btnBuscar = document.getElementById('btnBuscar');
    const inputCargo = document.getElementById('cargo');
    const inputCidade = document.getElementById('cidade');
    const checkBuscarProximas = document.getElementById('buscar_proximas');
    const resultadosVagasDiv = document.getElementById('resultadosVagas');
    const statusMessageDiv = document.getElementById('statusMessage');
    const paginationControlsDiv = document.getElementById('paginationControls');

    const API_BASE_URL = 'http://127.0.0.1:5000'; // URL da sua API Flask
    const VAGAS_POR_PAGINA_FRONTEND = 3; // Igual ao VAGAS_POR_PAGINA no backend para consistência inicial

    let todasAsVagasRecebidas = [];
    let paginaAtual = 0;

    btnBuscar.addEventListener('click', async () => {
        const cargo = inputCargo.value.trim();
        const cidade = inputCidade.value.trim();
        const buscarProximas = checkBuscarProximas.checked;

        if (!cargo || !cidade) {
            statusMessageDiv.textContent = 'Por favor, preencha o cargo e a cidade.';
            statusMessageDiv.style.color = 'red';
            return;
        }

        statusMessageDiv.textContent = 'Buscando vagas, por favor aguarde... (Isso pode levar alguns minutos)';
        statusMessageDiv.style.color = '#E2E8F0';
        resultadosVagasDiv.innerHTML = ''; // Limpa resultados anteriores
        paginationControlsDiv.innerHTML = ''; // Limpa paginação anterior
        todasAsVagasRecebidas = [];
        paginaAtual = 0;
        btnBuscar.disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/api/buscar-vagas`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cargo: cargo,
                    cidade_principal: cidade,
                    buscar_proximas: buscarProximas,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                statusMessageDiv.textContent = data.mensagem || 'Busca concluída.';
                statusMessageDiv.style.color = 'green';
                todasAsVagasRecebidas = data.vagas || [];
                if (todasAsVagasRecebidas.length > 0) {
                    mostrarPaginaDeVagas();
                } else {
                    resultadosVagasDiv.innerHTML = '<p>Nenhuma vaga encontrada com os critérios informados.</p>';
                }
            } else {
                statusMessageDiv.textContent = `Erro: ${data.erro || 'Ocorreu um erro na API.'}`;
                statusMessageDiv.style.color = 'red';
            }
        } catch (error) {
            console.error('Erro ao buscar vagas:', error);
            statusMessageDiv.textContent = 'Erro de conexão ou ao processar a busca. Tente novamente.';
            statusMessageDiv.style.color = 'red';
        } finally {
            btnBuscar.disabled = false;
        }
    });

    function mostrarPaginaDeVagas() {
        resultadosVagasDiv.innerHTML = ''; // Limpa para nova página
        const inicio = paginaAtual * VAGAS_POR_PAGINA_FRONTEND;
        const fim = inicio + VAGAS_POR_PAGINA_FRONTEND;
        const vagasDaPagina = todasAsVagasRecebidas.slice(inicio, fim);

        if (vagasDaPagina.length === 0 && paginaAtual === 0) {
            resultadosVagasDiv.innerHTML = '<p>Nenhuma vaga encontrada.</p>';
            paginationControlsDiv.innerHTML = '';
            return;
        }

        vagasDaPagina.forEach(vaga => {
            const vagaDiv = document.createElement('div');
            vagaDiv.classList.add('vaga');

            let dataFormatada = vaga.data_postagem_original || "Não informada";

            vagaDiv.innerHTML = `
                <h3>🎯 ${vaga.titulo || 'N/A'}</h3>
                <p><strong>🏢 Empresa:</strong> ${vaga.empresa || 'N/A'}</p>
                <p><strong>📍 Localização:</strong> ${vaga.localizacao || 'N/A'}</p>
                ${(vaga.salario && vaga.salario.toLowerCase() !== 'não informado') ? `<p><strong>💰 Salário:</strong> ${vaga.salario}</p>` : ''}
                <p><strong>🗓️ Postada em:</strong> ${dataFormatada}</p>
                ${(vaga.descricao_resumida && vaga.descricao_resumida.toLowerCase() !== 'não informado') ? `<p><strong>📝 Descrição:</strong> ${vaga.descricao_resumida}</p>` : ''}
                ${(vaga.link && vaga.link.toLowerCase() !== 'não informado') ? `<p><strong>🔗 Link:</strong> <a href="${vaga.link}" target="_blank">${vaga.link}</a></p>` : ''}
            `;
            resultadosVagasDiv.appendChild(vagaDiv);
        });
        renderizarControlesDePaginacao();
    }

    function renderizarControlesDePaginacao() {
        paginationControlsDiv.innerHTML = '';
        const totalPaginas = Math.ceil(todasAsVagasRecebidas.length / VAGAS_POR_PAGINA_FRONTEND);

        if (totalPaginas <= 1) return; // Não precisa de controles se for 1 página ou menos

        // Botão "Anterior"
        if (paginaAtual > 0) {
            const btnAnterior = document.createElement('button');
            btnAnterior.textContent = '⬅️ Anterior';
            btnAnterior.addEventListener('click', () => {
                paginaAtual--;
                mostrarPaginaDeVagas();
            });
            paginationControlsDiv.appendChild(btnAnterior);
        }

        // Indicador de página (simples)
        const pageIndicator = document.createElement('span');
        pageIndicator.textContent = ` Página ${paginaAtual + 1} de ${totalPaginas} `;
        pageIndicator.style.margin = "0 10px";
        paginationControlsDiv.appendChild(pageIndicator);

        // Botão "Próxima"
        if ((paginaAtual + 1) < totalPaginas) {
            const btnProxima = document.createElement('button');
            btnProxima.textContent = 'Próxima ➡️';
            btnProxima.addEventListener('click', () => {
                paginaAtual++;
                mostrarPaginaDeVagas();
            });
            paginationControlsDiv.appendChild(btnProxima);
        }
    }
});
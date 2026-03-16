const DATA_URL = './leaderboard_public.json';

const elements = {
  metricName: document.getElementById('metricName'),
  updatedAt: document.getElementById('updatedAt'),
  teamCount: document.getElementById('teamCount'),
  bestScore: document.getElementById('bestScore'),
  statusMessage: document.getElementById('statusMessage'),
  tableWrap: document.getElementById('tableWrap'),
  leaderboardBody: document.getElementById('leaderboardBody'),
  refreshButton: document.getElementById('refreshButton'),
};

function formatScore(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '-';
  return value.toFixed(6);
}

function formatUpdatedAt(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

function normalizePayload(payload) {
  if (Array.isArray(payload)) {
    return {
      metric: 'PR-AUC',
      updated_at: null,
      leaderboard: payload,
    };
  }

  return {
    metric: payload.metric || 'PR-AUC',
    updated_at: payload.updated_at || null,
    leaderboard: Array.isArray(payload.leaderboard) ? payload.leaderboard : [],
  };
}

function renderRows(rows) {
  elements.leaderboardBody.innerHTML = '';

  rows.forEach((row, index) => {
    const tr = document.createElement('tr');
    const rank = row.rank ?? index + 1;
    const team = row.team ?? '-';
    const score = typeof row.score === 'number' ? row.score : Number(row.score);

    tr.innerHTML = `
      <td><span class="rank-badge">${rank}</span></td>
      <td class="team-name">${team}</td>
      <td class="score">${formatScore(score)}</td>
    `;

    elements.leaderboardBody.appendChild(tr);
  });
}

function renderSummary(rows) {
  elements.teamCount.textContent = String(rows.length);
  const best = rows.length > 0 ? Number(rows[0].score) : NaN;
  elements.bestScore.textContent = formatScore(best);
}

function showError(message) {
  elements.statusMessage.textContent = message;
  elements.statusMessage.hidden = false;
  elements.tableWrap.hidden = true;
}

function showTable() {
  elements.statusMessage.hidden = true;
  elements.tableWrap.hidden = false;
}

async function loadLeaderboard() {
  elements.statusMessage.hidden = false;
  elements.statusMessage.textContent = '리더보드를 불러오는 중입니다...';
  elements.tableWrap.hidden = true;

  try {
    const response = await fetch(`${DATA_URL}?t=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = normalizePayload(await response.json());
    const rows = payload.leaderboard
      .map((row, index) => ({
        rank: row.rank ?? index + 1,
        team: row.team,
        score: typeof row.score === 'number' ? row.score : Number(row.score),
      }))
      .sort((a, b) => a.rank - b.rank);

    elements.metricName.textContent = payload.metric;
    elements.updatedAt.textContent = formatUpdatedAt(payload.updated_at);

    if (rows.length === 0) {
      showError('아직 표시할 제출 결과가 없습니다.');
      renderSummary([]);
      return;
    }

    renderRows(rows);
    renderSummary(rows);
    showTable();
  } catch (error) {
    console.error(error);
    showError('리더보드를 불러오지 못했습니다. leaderboard_public.json 파일과 권한 설정을 확인해주세요.');
    renderSummary([]);
  }
}

elements.refreshButton.addEventListener('click', loadLeaderboard);
document.addEventListener('DOMContentLoaded', loadLeaderboard);

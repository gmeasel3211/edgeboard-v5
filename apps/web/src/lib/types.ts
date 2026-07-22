export type User = {
  id: string;
  email: string;
  display_name: string;
  role: string;
  tier: "free" | "pro" | "elite";
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
};

export type Pick = {
  id: string;
  game_id: string;
  card_date: string;
  matchup: string;
  commence_time: string;
  market: string;
  selection: string;
  line: number | null;
  bookmaker: string;
  price: number;
  model_probability: number;
  market_probability: number;
  fair_odds: number;
  edge: number;
  expected_value: number;
  confidence: number;
  data_quality: number;
  score: number;
  grade: string;
  units: number;
  is_official: boolean;
  result: string | null;
  profit_units: number | null;
  clv: number | null;
  reasons: string[];
};

export type RecordSummary = {
  wins: number;
  losses: number;
  pushes: number;
  pending: number;
  units: number;
  units_risked: number;
  roi: number;
  win_rate: number;
  average_clv: number | null;
  total_official: number;
};

export type Dashboard = {
  as_of: string;
  tier: string;
  record: RecordSummary;
  official: Pick[];
  watchlist: Pick[];
  games: Array<{
    id: string;
    matchup: string;
    commence_time: string;
    venue: string | null;
    status: string;
    away_pitcher: string | null;
    home_pitcher: string | null;
    projected_score: { away: number | null; home: number | null };
    home_win_probability: number | null;
    data_quality: number | null;
  }>;
};

class NBAPlayer:
    def __init__(self, name, teamName, teamCity, link, status):
        self.name = name
        self.teamName = teamName
        self.teamCity = teamCity
        self.link = link
        self.status = status
        self.games = {
            'points': [],
            'rebounds': [],
            'assists': [],
            'three_pointers_made': []
        }
        self.benchmarks = {
            'points': [15, 20, 25, 30],
            'rebounds': [4, 6, 8, 10, 12],
            'assists': [4, 6, 8, 10, 12],
            'three_pointers_made': [2, 3, 4, 5]
        }

    def add_game_stats(self, points, rebounds, assists, three_pointers_made):
        self.games['points'].append(points)
        self.games['rebounds'].append(rebounds)
        self.games['assists'].append(assists)
        self.games['three_pointers_made'].append(three_pointers_made)

    def calculate_benchmark_frequency(self, stat, threshold):
        count = sum(1 for value in self.games[stat] if value >= threshold)
        return (count / len(self.games[stat])) * 100

    def get_all_benchmarks(self):
        all_benchmarks = {}
        for stat, thresholds in self.benchmarks.items():
            stat_benchmarks = {}
            for threshold in thresholds:
                frequency = self.calculate_benchmark_frequency(stat, threshold)
                stat_benchmarks[f"{threshold}+"] = frequency
            all_benchmarks[stat] = stat_benchmarks
        return all_benchmarks

    def print_benchmarks(self):
        all_benchmarks = self.get_all_benchmarks()
        print(f"{self.name} Benchmarks:")
        for stat, benchmarks in all_benchmarks.items():
            print(f"  {stat.capitalize()}:")
            for threshold, frequency in benchmarks.items():
                print(f"    {threshold}: {frequency:.2f}%")

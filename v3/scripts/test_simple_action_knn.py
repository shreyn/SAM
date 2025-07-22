from v3.utils.simple_action_knn import SimpleActionKNN


def main():
    knn = SimpleActionKNN(k=5)
    print("\nSimple Action KNN Test Console")
    print("Type a message and see the top K most similar actions. Type 'exit' to quit.\n")
    while True:
        user_input = input("Enter a message: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Exiting.")
            break
        if not user_input:
            continue
        top_actions = knn.get_top_k(user_input)
        print("\nTop actions:")
        for i, (action, score) in enumerate(top_actions, 1):
            print(f"  {i}. {action:15} | similarity: {score:.3f}")
        if len(top_actions) > 1:
            delta = top_actions[0][1] - top_actions[1][1]
            print(f"\nSimilarity delta between top 1 and 2: {delta:.3f}")
        print("")

if __name__ == "__main__":
    main() 
import random
import time

print("System Started")

while True:
    heart_rate = random.randint(60, 130)
    movement = random.randint(0, 1)

    print("Heart Rate:", heart_rate)
    print("Movement:", movement)

    if movement == 1:
        print("Impact detected!")

        fall_probability = random.random()
        print("Fall Probability:", round(fall_probability, 2))

        if fall_probability > 0.5:
            print("High fall probability!")

            # Multi-sensor fusion
            if heart_rate > 110:
                print("Physiological anomaly detected!")

                # STEP: False alarm prevention
                print("Cancel alert? (yes/no): ", end="")
                user_input = input()

                if user_input.lower() == "yes":
                    print("Alert cancelled.")
                else:
                    print("🚨 EMERGENCY ALERT SENT!")

            else:
                print("No physiological anomaly → false alarm")

        else:
            print("Low fall probability → ignore")

    else:
        print("No impact")

    print("-------------------")

    time.sleep(3)
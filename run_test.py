#import stuff
import requests
import concurrent.futures
import pandas as pd
import time
import sys

with open("api.txt", "r") as f:
  api = f.readlines()

url = api[0]

headers = {
    'Authorization': api[1],
    'Content-Type': 'application/json'
}

def run(system, user, model):
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]


def run_parallel(system, user, model, num_requests=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(run, system, user, model) for _ in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    return results


def do_test(model, case):
  print("\nTesting", case, "-"*40)
  overall_start_time = time.time()
  with open("texts.txt", "r") as f:
    texts = f.read().split("\n")
  texts = [text for text in texts if text]
  out_lens = [10, 100, 1000]
  n_jobs = [1, 4, 16, 64]
  nrep = 2
  results = []
  for i in range(nrep):
    for out_len in out_lens:
      for text in texts:
        for n_job in n_jobs:
          attempt = 0
          fail = True
          max_attempts = 10
          while attempt < max_attempts and fail:
              try:
                  start_time = time.time()
                  user  = f"You are a helpful assistant writing about the following TOPIC:\n\n'{text}'"
                  system = f"Write {out_len} words about the TOPIC."
                  out = "@@".join(run_parallel(user, system, model, n_job))
                  secs = time.time() - start_time
                  fail = False
              except Exception as e:
                  attempt += 1
                  if attempt == max_attempts:
                      raise e 
                  print(f"Retrying in {attempt} seconds...")
                  time.sleep(attempt)
          n_text = len(text.split(" "))
          result = [n_job, secs/n_job, n_text, out_len, len(out.split(" "))/n_job, out]
          print("\tn jobs: " + str(result[0]) + " - dur: " + str(round(result[1],1)) + " - input length: "  + str(result[2]) +  " - output length: " + str(result[3]))
          results.append(result)
  end_time = time.time()
  print(f"Finished running {case} in {round(end_time - overall_start_time, 1)} seconds")
  pd.DataFrame(results, columns=['n_jobs', 'secs', 'prompt_length','output_length_instruct','output_length','output']).to_csv("val/" + case + ".csv", index=False)



if __name__ == "__main__":
  
  args = sys.argv
  
  # test if argument was providded
  if len(args) < 2:
    print("Please provide the case to test")
    sys.exit(1)
    
  do_test(args[1], args[2])
  

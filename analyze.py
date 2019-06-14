#! /usr/bin/python3
import re
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
from pylab import *

kMaxInterval = 60

def AnalyzeRaw(datas):
  transfers = [0]
  bandwidths = [0]
  jitters = [0]
  lost_rates = [0]
  for data in datas:
    transfers.append(float(data[2]))
    bandwidth = data[3]
    if (data[4] == "Mbits"):
      bandwidth = float(bandwidth)*1024;
    bandwidths.append(float(bandwidth))
#    jitters.append(float(data[5]))
#    lost_rates.append(float(data[8]))
  return [np.mean(transfers), np.mean(bandwidths),
          np.median(transfers), np.median(bandwidths),
          np.amax(transfers), np.amax(bandwidths),
          np.amin(transfers), np.amin(bandwidths)]

# get value value of transfer data, bandwidth, jitter and lost rate.
def ParseFile(input):
  print("Parse "+input)
  results = []
  with open(input, 'r') as input_file:
    for line in input_file:
      result = ParseLine(line)
      if not result:
        continue

      results.append(result)
      if (float(result[0]) >= kMaxInterval - 1):
        break;
  return results;

def ParseLine(line):
  match_result = re.match(r"^\[.*?\]\s+"
                          "(\d+[.]\d*)\s*-\s*(\d+[.]\d*)\s+sec\s+"
                          "(\d+[.]{0,1}\d*) KBytes\s+"
                          "(\d+[.]{0,1}\d*) ([MK]bits)/sec", line)
#                          "(\d+[.]\d*) ms\s+"
#                          "(\d+)/\s+"
#                          "(\d+)\s+"
#                          "\((\d+[.]{0,1}\d*)\%\)$", line)
  if match_result == None:
#    print("Can't pasrse " + line);
    return match_result
  return match_result.groups()

def ParseDir(path, output_dir):
  file_list = os.listdir(path)
  analyze_results = []
  for i in range(0, len(file_list)):
    file_path = os.path.join(path, file_list[i])
    if os.path.isfile(file_path) and (file_list[i].find(".log") != -1):
      print(file_path)
      results = ParseFile(file_path)
      if (len(results) == 0):
        print("Parse "+file_path+"is empty!")
        continue
      analyze_results.append(AnalyzeRaw(results))
  
  title = ["transfer_mean", "bandwidth_mean",
          "transfer_median", "bandwidth_median",
          "transfer_max", "bandwidth_max",
          "transfer_min", "bandwidth_min"]
  output_path = os.path.join(output_dir, path+"_analyze.csv")
  with open(output_path, 'w+') as output_file:
    output_file.write(','.join(title))
    output_file.write('\n')
    for result in analyze_results:
      print(result)
      output_file.write(','.join('%.02f'%i for i in result))
      output_file.write('\n')

def AnalyzeMulticast():
  multicast_path_list = ["multicast_1M", "multicast_2M", "multicast_4M", "multicast_6M", "multicast_8M", "multicast_10M", "multicast_20M", "multicast_40M"]
  for path in multicast_path_list:
    ParseDir(path, "multicast");

def AnalyzeUDP():
  multicast_path_list = ["udp_1M", "udp_2M", "udp_4M", "udp_8M", "udp_20M", "udp_40M"]
  for path in multicast_path_list:
    ParseDir(path, "udp");

def AnalyzeTCP():
  multicast_path_list = ["tcp_1M", "tcp_2M", "tcp_4M", "tcp_8M", "tcp_10M", "tcp_20M"]
  for path in multicast_path_list:
    ParseDir(path, "tcp");

def ShowAllData(path):

  file_list = ["multicast_1M_analyze.csv", "multicast_2M_analyze.csv", "multicast_4M_analyze.csv", 
              "multicast_6M_analyze.csv", "multicast_8M_analyze.csv", "multicast_10M_analyze.csv", "multicast_20M_analyze.csv", "multicast_40M_analyze.csv"]
  bandwithds_mean = []
  lostrate_mean = []
  for i in range(0, len(file_list)):
    file_path = os.path.join("multicast", file_list[i])
    with open(file_path, 'r') as csvfile:
      reader = csv.DictReader(csvfile)
      column_bandwidths = [row["bandwidth_mean"] for row in reader]
      column_bandwidths = [float(value) for value in column_bandwidths]
      bandwithds_mean.append(np.mean(column_bandwidths))
    
    with open(file_path, 'r') as csvfile:
      reader = csv.reader(csvfile)
      column_lostrates = [row[3] for row in reader][1:]
      column_lostrates = [float(value) for value in column_lostrates]
      lostrate_mean.append(np.mean(column_lostrates))

  plt.figure(1)
  plt.subplot(221)
  plt.title("bandwidth")
  plt.plot([1,2,4,6,8,10,20,40], bandwithds_mean)
  xlim(1, 40)
  plt.subplot(222)
  plt.title("lost rates")
  plt.plot([1,2,4,6,8,10,20,40], lostrate_mean)
  xlim(1, 40)

  file_list = ["udp_1M_analyze.csv", "udp_2M_analyze.csv", "udp_4M_analyze.csv", 
              "udp_8M_analyze.csv", "udp_20M_analyze.csv", "udp_40M_analyze.csv"]
  udp_bandwithds_mean = []
  udp_lostrate_mean = []
  for i in range(0, len(file_list)):
    file_path = os.path.join("udp", file_list[i])
    with open(file_path, 'r') as csvfile:
      reader = csv.reader(csvfile)
      column_bandwidths = [row[1] for row in reader][1:]
      column_bandwidths = [float(value) for value in column_bandwidths]
      udp_bandwithds_mean.append(np.mean(column_bandwidths))
    
    with open(file_path, 'r') as csvfile:
      reader = csv.reader(csvfile)
      column_lostrates = [row[3] for row in reader][1:]
      column_lostrates = [float(value) for value in column_lostrates]
      udp_lostrate_mean.append(np.mean(column_lostrates))
  print(udp_bandwithds_mean)
  print(udp_lostrate_mean)
  plt.subplot(223)
  plt.title("bandwidth")
  plt.plot([1,2,4,8,20,40], udp_bandwithds_mean)
  xlim(1, 40)
  plt.subplot(224)
  plt.title("lost rates")
  plt.plot([1,2,4,8,20,40], udp_lostrate_mean)
  xlim(1, 40)

  file_list = ["tcp_1M_analyze.csv", "tcp_2M_analyze.csv", "tcp_4M_analyze.csv", 
              "tcp_8M_analyze.csv", "tcp_10M_analyze.csv", "tcp_20M_analyze.csv"]
  tcp_bandwithds_mean = []
  for i in range(0, len(file_list)):
    file_path = os.path.join("tcp", file_list[i])
    with open(file_path, 'r') as csvfile:
      reader = csv.reader(csvfile)
      column_bandwidths = [row[1] for row in reader][1:]
      column_bandwidths = [float(value) for value in column_bandwidths]
      tcp_bandwithds_mean.append(np.mean(column_bandwidths))
    
  print(tcp_bandwithds_mean)
  plt.subplot(223)
  plt.title("bandwidth")
  plt.plot([1,2,4,8,10,20], tcp_bandwithds_mean)
  xlim(1, 20)

  plt.show();

def show(input_bandwidths1, input_bandwidths2, mbandwidths, mlost_rates, ubandwidths, ulost_rates):
    plt.figure(1)
    plt.subplot(221)
    plt.title("bandwidth")
    plt.plot(input_bandwidths1, mbandwidths)
    xlim(1, 40)



    plt.subplot(223)
    plt.title("bandwidth")
    plt.plot(input_bandwidths2, ubandwidths)
    xlim(1, 40)

    plt.subplot(224)
    plt.title("lost rates")
    plt.plot(input_bandwidths2, ulost_rates)
    xlim(1, 40)

    plt.show();

if __name__ == '__main__':
#  AnalyzeTCP()
  ShowAllData("multicast")
#  show([0,40], np.array([10,1000]), np.array([20,50]))
#  multicast_path_list = ["multicast_1M"]
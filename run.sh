#!/bin/bash


#######   Define some colors to make the output fancy!  #############
C_RESET=""
C_RED=""
C_GREEN=""
C_YELLOW=""
C_WHITE=""
if echo "$*" | grep -v noColour > /dev/null 2>&1; then
    C_RESET="$(tput sgr0)"
    C_RED="$(tput bold)$(tput setab 0)$(tput setaf 1)"
    C_GREEN="$(tput bold)$(tput setab 0)$(tput setaf 2)"
    C_YELLOW="$(tput bold)$(tput setab 0)$(tput setaf 3)"
    C_WHITE="$(tput bold)$(tput setab 0)$(tput setaf 7)"
fi

#######   Check if the input is valid or not ###########
list_do_not_contain() {
  for word in $1; do
    [[ $word = $2 ]] && return 1
  done
  return 0
}

list="LS2 LS2_greedy"

######  main  part #######

## check the number of parameter 
if [[ $# -ne 4 ]]; then
    echo "${C_RED}Usage:${C_RESET} $0 ${C_GREEN}  input_file_name  cutoff_time  choice(LS2|LS2_greedy)  integer_seed ${C_RESET}"
    exit
fi


echo "first parameter: $1"
echo "second parameter: $2"
echo "third parameter: $3"
echo "fourth parameter: $4"

input_file_name=$1
cutoff_time=$2
choice=$3
seed=$4

## check the format of 'choice'
if  list_do_not_contain  "$list"  "$choice"; then 
    echo "${C_RED}Error:${C_RESET}  ${C_YELLOW}$choice ${C_RESET} should be one of: ${C_GREEN} $list ${C_RESET} "
    exit
fi

## check the format of 'seed'

if [[ $seed =~ ^-?[0-9]+$ ]]; then
    echo "Will run the cmd: ${C_GREEN}java numvc  $input_file_name  $cutoff_time   $choice  $seed${C_RESET}"
    # to run java, please uncomment (remove the #) the following line
    javac numvc.java
    java numvc  $input_file_name  $cutoff_time   $choice  $seed 
else
    echo "${C_RED}Error:${C_RESET} ${C_YELLOW}seed ${C_RESET} should be an integer, but given one is ${C_YELLOW} $seed ${C_RESET}"
    exit
fi

echo "${C_GREEN}Status ${C_RESET}: starting to run successfully..."


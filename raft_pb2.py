# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\x12\x04raft\"4\n\x08LogEntry\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\t\"\xcd\x02\n\x12\x41ppendEntryRequest\x12\x11\n\x04term\x18\x01 \x01(\x05H\x00\x88\x01\x01\x12\x16\n\tleader_id\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x1b\n\x0eprev_log_index\x18\x03 \x01(\x05H\x02\x88\x01\x01\x12\x1a\n\rprev_log_term\x18\x04 \x01(\x05H\x03\x88\x01\x01\x12\x11\n\x04type\x18\x05 \x01(\x05H\x04\x88\x01\x01\x12\x1a\n\rleader_commit\x18\x06 \x01(\x05H\x05\x88\x01\x01\x12\x1b\n\x0elease_duration\x18\x07 \x01(\x03H\x06\x88\x01\x01\x12\x1d\n\x05\x65ntry\x18\x08 \x03(\x0b\x32\x0e.raft.LogEntryB\x07\n\x05_termB\x0c\n\n_leader_idB\x11\n\x0f_prev_log_indexB\x10\n\x0e_prev_log_termB\x07\n\x05_typeB\x10\n\x0e_leader_commitB\x11\n\x0f_lease_duration\"y\n\x13\x41ppendEntryResponse\x12\x11\n\x04term\x18\x01 \x01(\x05H\x00\x88\x01\x01\x12\x14\n\x07success\x18\x02 \x01(\x08H\x01\x88\x01\x01\x12\x16\n\tleader_id\x18\x03 \x01(\tH\x02\x88\x01\x01\x42\x07\n\x05_termB\n\n\x08_successB\x0c\n\n_leader_id\"\x80\x02\n\x12RequestVoteRequest\x12\x11\n\x04term\x18\x01 \x01(\x05H\x00\x88\x01\x01\x12\x19\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x1b\n\x0elast_log_index\x18\x03 \x01(\x05H\x02\x88\x01\x01\x12\x1a\n\rlast_log_term\x18\x04 \x01(\x05H\x03\x88\x01\x01\x12&\n\x19old_leader_lease_duration\x18\x05 \x01(\x03H\x04\x88\x01\x01\x42\x07\n\x05_termB\x0f\n\r_candidate_idB\x11\n\x0f_last_log_indexB\x10\n\x0e_last_log_termB\x1c\n\x1a_old_leader_lease_duration\"\x83\x01\n\x13RequestVoteResponse\x12\x11\n\x04term\x18\x01 \x01(\x05H\x00\x88\x01\x01\x12\x19\n\x0cvote_granted\x18\x02 \x01(\x08H\x01\x88\x01\x01\x12\x16\n\tleader_id\x18\x03 \x01(\tH\x02\x88\x01\x01\x42\x07\n\x05_termB\x0f\n\r_vote_grantedB\x0c\n\n_leader_id\"k\n\x12ServeClientRequest\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x10\n\x03key\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x12\n\x05value\x18\x03 \x01(\tH\x01\x88\x01\x01\x12\x0f\n\x07\x61\x64\x64ress\x18\x04 \x01(\tB\x06\n\x04_keyB\x08\n\x06_value\"y\n\x13ServeClientResponse\x12\x11\n\x04\x64\x61ta\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x16\n\tleader_id\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x14\n\x07success\x18\x03 \x01(\x08H\x02\x88\x01\x01\x42\x07\n\x05_dataB\x0c\n\n_leader_idB\n\n\x08_success2\xd9\x01\n\x0bRaftService\x12\x42\n\x0b\x41ppendEntry\x12\x18.raft.AppendEntryRequest\x1a\x19.raft.AppendEntryResponse\x12\x42\n\x0bRequestVote\x12\x18.raft.RequestVoteRequest\x1a\x19.raft.RequestVoteResponse\x12\x42\n\x0bServeClient\x12\x18.raft.ServeClientRequest\x1a\x19.raft.ServeClientResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_LOGENTRY']._serialized_start=20
  _globals['_LOGENTRY']._serialized_end=72
  _globals['_APPENDENTRYREQUEST']._serialized_start=75
  _globals['_APPENDENTRYREQUEST']._serialized_end=408
  _globals['_APPENDENTRYRESPONSE']._serialized_start=410
  _globals['_APPENDENTRYRESPONSE']._serialized_end=531
  _globals['_REQUESTVOTEREQUEST']._serialized_start=534
  _globals['_REQUESTVOTEREQUEST']._serialized_end=790
  _globals['_REQUESTVOTERESPONSE']._serialized_start=793
  _globals['_REQUESTVOTERESPONSE']._serialized_end=924
  _globals['_SERVECLIENTREQUEST']._serialized_start=926
  _globals['_SERVECLIENTREQUEST']._serialized_end=1033
  _globals['_SERVECLIENTRESPONSE']._serialized_start=1035
  _globals['_SERVECLIENTRESPONSE']._serialized_end=1156
  _globals['_RAFTSERVICE']._serialized_start=1159
  _globals['_RAFTSERVICE']._serialized_end=1376
# @@protoc_insertion_point(module_scope)
